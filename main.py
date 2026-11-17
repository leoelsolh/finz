#!/usr/bin/python3
#
#          [ Finz Surf Rental ]
#
# Main script. Handles app config and connects
# the frontend to the backend. 'db.' and 'config.'
# prefixes to fetch and handle database and config
# logic. Database helpers are seperate from this 
# script, you can view SQL ops in 'db.py'

import time
import hmac
import secrets
import logging
import datetime

from flask import Flask
from flask import flash
from flask import render_template
from flask import abort
from flask import request
from flask import redirect
from flask import session
from flask import url_for
from zoneinfo import ZoneInfo
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash

import db
import config
import schema

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)
app.secret_key = config.SECRET_KEY

app.config['SESSION_COOKIE_SAMESITE'] = config.SESSION_COOKIE_SAMESITE
app.config['SESSION_COOKIE_SECURE'] = config.SESSION_COOKIE_SECURE
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

app.permanent_session_lifetime = datetime.timedelta(hours=config.SESSION_LIFETIME_HOURS)
logging.basicConfig(level=logging.INFO)

schema.run_migrations()
login_attempts = {}

def get_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']

@app.context_processor
def inject_csrf_token():
    return {'csrf_token': get_csrf_token()}

@app.context_processor
def inject_shop_details():
    return {'shop_phone': config.SHOP_PHONE, 'shop_email': config.SHOP_EMAIL}

@app.template_filter('shoptime')
def shoptime(value):
    ldn_time = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).astimezone(ZoneInfo(config.SHOP_TIMEZONE))
    return ldn_time.strftime('%H:%M')

# Site logic
@app.before_request
def check_auth_session():
    if request.path.startswith('/admin'):
        if request.path == '/admin/login':
            return 

        if not session.get('name'):
            return redirect(url_for('admin_login'))

@app.before_request
def check_csrf_token():
    if request.method == 'POST':
        token = session.get('csrf_token')
        form_token = request.form.get('csrf_token')

        if not token or not form_token or not hmac.compare_digest(token, form_token):
            abort(403)

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

@app.errorhandler(db.DatabaseError)
def handle_database_error(error):
    return render_template('error.html'), 503

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

# Admin pages
@app.route('/admin')
def admin():
    search = request.args.get('q')
    out_total = len(db.get_active_rentals())
    rentals = db.get_active_rentals(search)
    board_stock = db.get_available_boards()
    bookings = db.get_todays_bookings()

    return render_template('admin.html', out_total=out_total, rentals=rentals, search=search, board_stock=board_stock, bookings=bookings)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        ip = request.remote_addr
        now = time.time()
        recent = [attempt for attempt in login_attempts.get(ip, []) if now - attempt < config.LOGIN_WINDOW_SECONDS]
        login_attempts[ip] = recent 

        # Ratelimit logic
        if len(recent) >= config.MAX_LOGIN_ATTEMPTS:
            return render_template('login.html', error='Too many attempts. Try again later.'), 429

        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return render_template('login.html', error='Both fields are required')
 
        # Success logic
        username_ok = hmac.compare_digest(username, config.ADMIN_USER)
        password_ok = check_password_hash(config.ADMIN_HASH, password)

        if username_ok and password_ok:
            login_attempts.pop(ip, None)
            session.permanent = True
            session['name'] = username 
            return redirect(url_for('admin'))

        login_attempts[ip].append(now)
        return render_template('login.html', error='wrong username or password'), 401

    return render_template('login.html')

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/admin/return', methods=['POST'])
def admin_return():
    rental_ids = request.form.getlist('rental_id')
    damaged_ids = request.form.getlist('damaged')

    if not rental_ids:
        flash('Nothing to return')
        return redirect(url_for('admin'))

    for rental_id in rental_ids:
        if rental_id in damaged_ids:
            damaged = 1
        else:
            damaged = 0
        db.mark_board_in(rental_id, damaged)
        
    return redirect(url_for('admin'))

@app.route('/admin/out', methods=['POST'])
def admin_out():
    item_ids = []
    for row in db.get_available_boards():
        raw = request.form.get(f'qty_{str(row['id'])}')
        qty = int(raw) if raw else 0
        item_ids += [row['id']] * qty 

    renter_name = request.form.get('renter_name')
    booking_id = request.form.get('booking_id')

    if not renter_name or not item_ids:
        flash('Please enter all required fields')
        return redirect(url_for('admin'))
    
    db.mark_hire_out(item_ids, renter_name)

    if booking_id:
        db.mark_booking_fulfilled(booking_id)
    
    return redirect(url_for('admin'))

@app.route('/admin/booking/edit', methods=['POST'])
def admin_edit_booking():
    booking_id = request.form.get('booking_id')
    board_qty = request.form.get('board_qty')

    if not booking_id or not board_qty:
        flash('Please enter all fields')
        return redirect(url_for('admin'))
    try:
        board_amount = int(board_qty)
        
        if board_amount < 1:
            flash('Board quantity cant be negative')
            return redirect(url_for('admin'))

    except ValueError:
        flash('Please enter a valid integer for board quantity. For example, "5" not "Five"')
        return redirect(url_for('admin'))

    db.update_booking(booking_id, board_amount)
    return redirect(url_for('admin'))

@app.route('/admin/stock')
def admin_stock():
    all_boards = db.get_all_boards()
    damaged_boards = db.get_damaged_boards()
    return render_template('stock.html', all_boards=all_boards, damaged_boards=damaged_boards)

@app.route('/admin/stock/add', methods=['POST'])
def admin_add_stock():
    name = request.form.get('name')
    size = request.form.get('size')
    price = request.form.get('price')
    quantity = request.form.get('quantity')
    category = request.form.get('category')
    if not name or not size or not price or not quantity or not category:
        flash('Please enter all fields')
        return redirect(url_for('admin'))

    if category not in ('surfboard', 'wetsuit', 'bodyboard'):
        flash('Invalid category.')
        return redirect(url_for('admin'))

    try:
        price = int(price)
        quantity = int(quantity)
        db.add_new_board(name, size, price, quantity, category)

    except ValueError:
        flash('Please enter a valid Integer Number.')
        return redirect(url_for('admin'))

    return redirect(url_for('admin'))

@app.route('/admin/stock/archive', methods=['POST'])
def admin_archive_stock():
    board_id = request.form.get('board_id')
    if not board_id:
        flash('Please enter all fields')
        return redirect(url_for('admin'))
    
    db.archive_board(board_id)
    return redirect(url_for('admin'))

@app.route('/admin/stock/quantity', methods=['POST'])
def admin_stock_quantity():
    board_id = request.form.get('board_id')
    quantity = request.form.get('quantity')

    if not board_id or not quantity:
        flash('Please enter all fields')
        return redirect(url_for('admin'))

    quantity = int(quantity)
    if quantity < 0:
        flash('Stock cant go negative...')
        return redirect(url_for('admin'))

    try: 
        quantity = int(quantity)
        db.set_board_quantity(quantity, board_id)

    except ValueError:
        flash('Please make sure the quantity is a valid number. For example "2", not "Two".')
        return redirect(url_for('admin'))
    
    return redirect(url_for('admin'))

@app.route('/admin/repair', methods=['POST'])
def admin_repair():
    board_id = request.form.get('board_id')
    if not board_id:
        flash('Please enter all fields')
        return redirect(url_for('admin'))

    db.clear_damage_from_board(board_id)
    return redirect(url_for('admin'))

@app.route('/admin/analytics')
def admin_analytics():
    period = request.args.get('period')
    periods = {'1W': 7, '1M': 30, '1Y': 365}
    if period not in periods:
        period = '1W'
    
    days = periods[period]
    cutoff = (datetime.datetime.now(ZoneInfo(config.SHOP_TIMEZONE)) - datetime.timedelta(days=days)).strftime('%Y-%m-%d')

    income = db.get_income_since(cutoff)
    bookings_count = db.get_bookings_count_since(cutoff)
    hires_per_day = db.get_hires_per_day_since(cutoff)
    return render_template('analytics.html', period=period, income=income, bookings_count=bookings_count, hires_per_day=hires_per_day)

# User-facing pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/book', methods=['GET', 'POST'])
def booking():
    if request.method == 'POST':

        if request.form.get('website'): # Silently drop requests that fill out hidden field
            flash('Your booking has been processed. Thank you.')
            return redirect(url_for('booking'))

        booking_name = request.form.get('name')
        booking_number = request.form.get('phone')
        booking_email = request.form.get('email')
        booking_date = request.form.get('hire_date')
        board_qty = request.form.get('board_qty')

        try: 
            board_qty = int(board_qty)
            if board_qty < 1:
                return render_template('book.html', error='Quantity can not be negative')
        except ValueError:
            return render_template('book.html', error='Please fill in a valid quantity number, like "2", not "two"')

        sizes = db.get_board_sizes()
        if not booking_name or not booking_date or not booking_number or not board_qty:
            return render_template('book.html', sizes=sizes, error='Please fill in the required fields')

        try:
            parsed_date = datetime.datetime.strptime(booking_date, '%Y-%m-%d').date()
        except ValueError:
            return render_template('book.html', sizes=sizes, error='Please enter a valid date')

        if parsed_date < datetime.datetime.now(ZoneInfo(config.SHOP_TIMEZONE)).date():
            return render_template('book.html', sizes=sizes, error='Hire date cannot be in the past')

        try:
            db.add_booking(booking_name, booking_number, booking_email, booking_date, board_qty)
            flash('Your booking has been processed. Thank you.')
            return redirect(url_for('booking'))
        except db.DatabaseError:
            return render_template('book.html', sizes=sizes, error='Something went wrong, Try again shortly'), 500

    if request.method == 'GET':
        sizes = db.get_board_sizes()
        return render_template('book.html', sizes=sizes)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/ourwork')
def our_work():
    return render_template('our_work.html')

@app.route('/hours')
def hours():
    return render_template('hours.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# main
if __name__ == '__main__': 
    app.run(debug=False)