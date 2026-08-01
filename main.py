#!/usr/bin/python3
import time
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
from werkzeug.security import check_password_hash

import db
import config
import schema

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.permanent_session_lifetime = datetime.timedelta(hours=8)
logging.basicConfig(level=logging.INFO)

schema.init_db() #Init database tables
login_attempts = {}

# Site logic
@app.before_request
def check_auth_session(): #Preproccessing
    if request.path.startswith('/admin'):
        if request.path == '/admin/login':
            return 

        if not session.get('name'):
            return redirect(url_for('admin_login'))

@app.errorhandler(db.DatabaseError)
def handle_database_error(error):
    return render_template('error.html'), 503

# Admin pages
@app.route('/admin')
def admin(): #admin dashboard
    rentals = db.get_active_rentals()
    board_stock = db.get_available_boards()
    bookings = db.get_todays_bookings()

    return render_template('admin.html', rentals=rentals, board_stock=board_stock, bookings=bookings)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        ip = request.remote_addr
        now = time.time()
        recent = [attempt for attempt in login_attempts.get(ip, []) if now - attempt < 3600]
        login_attempts[ip] = recent 

        # Ratelimit logic
        if len(recent) >= 5:
            return render_template('login.html', error='Too many attempts. Try again later.'), 429

        username = request.form['username']
        password = request.form['password']
 
        # Success logic
        username_ok = username == config.ADMIN_USER
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
def admin_return(): #mark a board as retuned
    marked_board = request.form['board_id']
    db.mark_board_in(marked_board)
    return redirect(url_for('admin'))

@app.route('/admin/out', methods=['POST'])
def admin_out(): #mark a board as gone out
    board_id = request.form['board_id']
    renter_name = request.form['renter_name']
    db.mark_board_out(board_id, renter_name)
    return redirect(url_for('admin'))

# User-facing pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/boards')
def boards(): #disaply all boards
    board_stock = db.get_all_boards()
    return render_template('boards.html', board_stock=board_stock)

@app.route('/boards/<int:board_id>')
def show_board(board_id): #view single board by its ID
    board = db.get_board_by_id(board_id)
    if board is None:
        abort(404)
    return render_template('board.html', board=board)

@app.route('/book', methods=['GET', 'POST'])
def booking(): #book a board
    if request.method == 'POST':

        booking_name = request.form['name']
        booking_number = request.form['phone']
        booking_email = request.form.get('email')
        booking_size = request.form['size_requested']
        booking_wetsuit = 1 if request.form.get('wetsuit') else 0
        booking_date = request.form['hire_date']

        if not booking_name or not booking_date or not booking_size:
            sizes = db.get_board_sizes()
            return render_template('book.html', sizes=sizes, error='Please fill in the required fields')

        try:
            db.add_booking(booking_name, booking_number, booking_email, booking_wetsuit, booking_date, booking_size)
            flash('Your booking has been processed. Thank you.')
            return redirect(url_for('booking'))
            
        except db.DatabaseError:
            #flash('Something went wrong, try again shortly')
            return render_template('book.html', sizes=[], error='Something went wrong, Try again shortly'), 500

    if request.method == 'GET':
        sizes = db.get_board_sizes()
        return render_template('book.html', sizes=sizes)

@app.route('/hours')
def hours():
    return render_template('hours.html')

# main
if __name__ == '__main__': 
    app.run(debug=False)