#!/usr/bin/python3
import time
import sqlite3
import logging
import datetime
import contextlib

from flask import Flask
from flask import flash
from flask import render_template
from flask import abort
from flask import request
from flask import redirect
from flask import session
from flask import url_for
from zoneinfo import ZoneInfo
from werkzeug.security import check_password_hash

import config
import schema

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.permanent_session_lifetime = datetime.timedelta(hours=8)
logging.basicConfig(level=logging.INFO)

schema.init_db() #Init database tables
login_attempts = {}

class DatabaseError(Exception):
    '''Raised when a database operation fails.'''

# Site logic
@app.errorhandler(DatabaseError)
def handle_database_error(error):
    return render_template('error.html'), 503

@contextlib.contextmanager
def get_connection():
    connection = sqlite3.connect(config.DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()

@app.before_request
def check_auth_session(): #Preproccessing
    if request.path.startswith('/admin'):
        if request.path == '/admin/login':
            return 

        if not session.get('name'):
            return redirect(url_for('admin_login'))


# Site helpers
def get_board_by_id(board_id):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''SELECT * FROM boards WHERE id = ?''', (board_id,))
            return cursor.fetchone() 

    except sqlite3.OperationalError as op_error:
        logging.exception('Failed to fetch board')
        raise DatabaseError('Could not fetch board') from op_error

def get_all_boards():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''SELECT * FROM boards''')
            return cursor.fetchall()

    except sqlite3.OperationalError as op_error:
        logging.exception('Failed to fetch boards')
        raise DatabaseError('Could not fetch boards') from op_error

def get_board_sizes():
    try: 
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''SELECT DISTINCT size FROM boards''')
            return cursor.fetchall()

    except sqlite3.OperationalError as op_error:
        logging.exception('Failed to fetch boards by size')
        raise DatabaseError('Could not fetch boards by size') from op_error

def add_booking(name, phone, email, wetsuit, hire_date, size):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''
                INSERT INTO bookings (name, phone, email, wetsuit, hire_date, size_requested) VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, phone, email, wetsuit, hire_date, size))

            connection.commit()

    except sqlite3.Error as error:
        logging.exception('Failed to add booking')
        raise DatabaseError('Could not save booking') from error

def get_available_boards():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''
                SELECT * FROM boards
                WHERE id NOT IN (
                    SELECT board_id FROM rentals 
                    WHERE came_back IS NULL
                    AND date(went_out) = date('now')
                )
            ''')
            return cursor.fetchall()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to fetch available boards')
        raise DatabaseError('Could not fetch available boards') from sql_error


# Admin logic
def mark_board_out(board_id, renter_name):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            
            went_out = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO rentals (went_out, board_id, name_booked) VALUES (?, ?, ?)
            ''', (went_out, board_id, renter_name))
            
            connection.commit()
    
    except sqlite3.Error as sql_error:
        logging.exception('Failed to mark board out')
        raise DatabaseError('Could not mark board out') from sql_error

def mark_board_in(board_id):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            came_back = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE rentals SET came_back = ? WHERE board_id = ? AND came_back IS NULL
                ''', (came_back, board_id))
            connection.commit()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to mark board in')
        raise DatabaseError('Could not mark board in') from sql_error

def get_active_rentals():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''
                SELECT boards.id AS board_id, boards.name, boards.size, rentals.name_booked, rentals.went_out
                FROM rentals
                JOIN boards ON rentals.board_id = boards.id
                WHERE came_back IS NULL
            ''')
            return cursor.fetchall()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to fetch active rentals')
        raise DatabaseError('Could not fetch active rentals') from sql_error

def get_todays_bookings():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            today = datetime.datetime.now(ZoneInfo(config.SHOP_TIMEZONE)).strftime('%Y-%m-%d')
            cursor.execute('''SELECT * FROM bookings WHERE hire_date = ?''', (today,))
            return cursor.fetchall()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to get todays bookings')
        raise DatabaseError('Could not get todays bookings') from sql_error


# Admin pages
@app.route('/admin')
def admin(): #admin dashboard
    rentals = get_active_rentals()
    board_stock = get_available_boards()
    bookings = get_todays_bookings()

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
    mark_board_in(marked_board)
    return redirect(url_for('admin'))

@app.route('/admin/out', methods=['POST'])
def admin_out(): #mark a board as gone out
    board_id = request.form['board_id']
    renter_name = request.form['renter_name']
    mark_board_out(board_id, renter_name)
    return redirect(url_for('admin'))

# Page return logic
@app.route('/preview-error')
def previewError():
    raise DatabaseError('Preview')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/boards')
def boards(): #disaply all boards
    board_stock = get_all_boards()
    return render_template('boards.html', board_stock=board_stock)

@app.route('/boards/<int:board_id>')
def show_board(board_id): #view single board by its ID
    board = get_board_by_id(board_id)
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
            sizes = get_board_sizes()
            return render_template('book.html', sizes=sizes, error='Please fill in the required fields')

        try:
            add_booking(booking_name, booking_number, booking_email, booking_wetsuit, booking_date, booking_size)
            flash('Your booking has been processed. Thank you.')
            return redirect(url_for('booking'))
            
        except DatabaseError:
            #flash('Something went wrong, try again shortly')
            return render_template('book.html', sizes=[], error='Something went wrong, Try again shortly'), 500

    if request.method == 'GET':
        sizes = get_board_sizes()
        return render_template('book.html', sizes=sizes)

@app.route('/hours')
def hours():
    return render_template('hours.html')

# main
if __name__ == '__main__': 
    app.run(debug=False)