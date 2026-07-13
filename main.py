#!/usr/bin/python3
import sqlite3
import datetime
from flask import Flask
from flask import render_template
from flask import abort
from flask import request

app = Flask(__name__)

# database
try:
    with sqlite3.connect("rental.db") as database:
        cursor = database.cursor()

        # tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS boards (
                id    INTEGER PRIMARY KEY,
                name  TEXT,
                size  TEXT,
                price INTEGER
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id          INTEGER PRIMARY KEY,
                name        TEXT,
                phone       TEXT,
                email       TEXT,
                wetsuit     INTEGER,
                hire_date    TEXT,
                size_requested TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rentals (
                id          INTEGER PRIMARY KEY,
                board_id    INTEGER,
                name_booked TEXT,
                went_out    TEXT,
                came_back   TEXT
            )
        ''')

except sqlite3.Error as error:
    raise Exception(f"\nCant fetch boards:\n{error}\n")

# Site helpers
def get_board_by_id(board_id):
    try:
        connection = sqlite3.connect("rental.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM boards WHERE id = ?''', (board_id,))
        
        return cursor.fetchone() 

    except sqlite3.OperationalError as op_error:
        print(f"\nError in this operation:\n{op_error}\n")

def get_all_boards():
    try:
        connection = sqlite3.connect("rental.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM boards''')

        return cursor.fetchall()
    except sqlite3.OperationalError as op_error:
        print(f"\nError fetching boards:\n{op_error}\n")

def get_board_sizes():
    try: 
        connection = sqlite3.connect("rental.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute('''SELECT DISTINCT size FROM boards''')

        return cursor.fetchall()
    except sqlite3.OperationalError as op_error:
        print(f"\nError fetching sizes:\n{op_error}\n")

def add_booking(name, phone, email, wetsuit, hire_date, size):
    try:
        with sqlite3.connect("rental.db") as connection:
            cursor = connection.cursor()

            cursor.execute('''
                INSERT INTO bookings (name, phone, email, wetsuit, hire_date, size_requested) VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, phone, email, wetsuit, hire_date, size))

    except sqlite3.Error as error:
        print(f"\nError in fetching form values:\n{error}\n")

def mark_board_out(board_id, renter_name):
    try:
        with sqlite3.connect("rental.db") as connection:
            cursor = connection.cursor()
            
            went_out = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                INSERT INTO rentals (went_out, board_id, name_booked) VALUES (?, ?, ?)
            ''', (went_out, board_id, renter_name))
    
    except sqlite3.Error as sql_error:
        print(f"\nSQL error inserting rental time-stamp:\n{sql_error}\n")

def mark_board_in(board_id):
    try:
        with sqlite3.connect("rental.db") as connection:
            cursor = connection.cursor()

            came_back = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute('''
                UPDATE rentals SET came_back = ? WHERE board_id = ? AND came_back IS NULL
                ''', (came_back, board_id))

    except sqlite3.Error as sql_error:
        print(f"\nSQL error closing rental time-stamp:\n{sql_error}\n")

# Page return logic
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/boards")
def boards():
    all_boards = get_all_boards()
    return render_template("boards.html", boards=all_boards) 

@app.route("/boards/<int:board_id>")
def show_board(board_id):
    board = get_board_by_id(board_id)
    if board is None:
        abort(404)
    return render_template("board.html", board=board)

@app.route("/book", methods=["GET", "POST"])
def booking():

    if request.method == "POST":
        booking_name = request.form["name"]
        booking_number = request.form["phone"]
        booking_email = request.form["email"]
        booking_size = request.form["size_requested"]
        booking_wetsuit = 1 if request.form.get("wetsuit") else 0 # If wetsuit is unticked, this will prevent an error since an unticked checkbox returns empty instead of false.
        booking_date = request.form["hire_date"]
    
        add_booking(booking_name, booking_number, booking_email, booking_wetsuit, booking_date, booking_size)

        return f"Your booking has been processed. Thank you."
        
    if request.method == "GET":
        sizes = get_board_sizes()
        return render_template("book.html", sizes=sizes)

@app.route("/hours")
def hours():
    return "No hours yet"

# main
if __name__ == '__main__': 
    app.run(debug=True)