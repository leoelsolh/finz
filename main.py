#!/usr/bin/python3
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
app.permanent_session_lifetime = datetime.timedelta(hours=config.SESSION_LIFETIME_HOURS)
logging.basicConfig(level=logging.INFO)

schema.init_db()
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

# Admin pages
@app.route('/admin')
def admin():
    rentals = db.get_active_rentals()
    board_stock = db.get_available_boards()
    bookings = db.get_todays_bookings()

    return render_template('admin.html', rentals=rentals, board_stock=board_stock, bookings=bookings)

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
    return redirect(url_for('admin'))

@app.route('/admin/return', methods=['POST'])
def admin_return():
    marked_board = request.form.get('rental_id')
    damaged = 1 if request.form.get('damaged') else 0
    damage_note = request.form.get('damage_note')

    if not marked_board:
        flash('A board must be selected')
        return redirect(url_for('admin'))

    db.mark_board_in(marked_board, damaged, damage_note)
    return redirect(url_for('admin'))

@app.route('/admin/out', methods=['POST'])
def admin_out():
    board_id = request.form.get('board_id')
    renter_name = request.form.get('renter_name')
    if not board_id or not renter_name:
        flash('Please enter all fields')
        return redirect(url_for('admin'))

    db.mark_board_out(board_id, renter_name)
    return redirect(url_for('admin'))

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
        booking_size = request.form.get('size_requested')
        booking_wetsuit = 1 if request.form.get('wetsuit') else 0
        booking_date = request.form.get('hire_date')

        sizes = db.get_board_sizes()
        if not booking_name or not booking_date or not booking_size or not booking_number:
            return render_template('book.html', sizes=sizes, error='Please fill in the required fields')

        try:
            parsed_date = datetime.datetime.strptime(booking_date, '%Y-%m-%d').date()
        except ValueError:
            return render_template('book.html', sizes=sizes, error='Please enter a valid date')

        if parsed_date < datetime.datetime.now(ZoneInfo(config.SHOP_TIMEZONE)).date():
            return render_template('book.html', sizes=sizes, error='Hire date cannot be in the past')

        try:
            db.add_booking(booking_name, booking_number, booking_email, booking_wetsuit, booking_date, booking_size)
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