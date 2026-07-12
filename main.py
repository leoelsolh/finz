#!/usr/bin/python3
import sqlite3
from flask import Flask
from flask import render_template
from flask import abort
from flask import request

app = Flask(__name__)

# database
try:
    with sqlite3.connect("rental.db") as database:
        cursor = database.cursor()
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
except sqlite3.Error as error:
    raise Exception(f"Cant fetch boards: {error}")

# Site helpers
def get_board_by_id(board_id):
    try:
        connection = sqlite3.connect("rental.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM boards WHERE id = ?''', (board_id,))
        
        return cursor.fetchone() 

    except sqlite3.OperationalError as op_error:
        print(f"Error in this operation: {op_error}")

def get_all_boards():
    try:
        connection = sqlite3.connect("rental.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM boards''')

        return cursor.fetchall()
    except sqlite3.OperationalError as op_error:
        print(f"Error fetching boards: {op_error}")

def get_board_sizes():
    try: 
        connection = sqlite3.connect("rental.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute('''SELECT DISTINCT size FROM boards''')

        return cursor.fetchall()
    except sqlite3.OperationalError as op_error:
        print(f"Error fetching sizes: {op_error}")

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
        size = request.form["board_size"]
        return f"<h3>Board size {size} booked.</h3>"
    
    if request.method == "GET":
        sizes = get_board_sizes()
        return render_template("book.html", sizes=sizes)

@app.route("/hours")
def hours():
    return "No hours yet"

# main
if __name__ == "__main__": 
    app.run(debug=True)