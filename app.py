#!/usr/bin/python3
import sqlite3
from flask import Flask
from flask import render_template
from flask import abort
from flask import request

app = Flask(__name__)

# database
database = sqlite3.connect("rental.db")
cursor = database.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS boards (
        id    INTEGER PRIMARY KEY,
        name  TEXT,
        size  TEXT,
        price INTEGER
    )
""")

all_boards = [
    {"ID": 1, "name": "Swirl", "size": "8'0", "price": 50},
    {"ID": 2, "name": "Hardboard", "size": "6'5", "price": 80},
    {"ID": 3, "name": "Oz", "size": "9'0", "price": 60},
    {"ID": 4, "name": "Max", "size": "9'0", "price": 60},
]

# Site routes
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/boards")
def boards():
    return render_template("boards.html", boards=all_boards) 

@app.route("/boards/<int:board_id>")
def show_board(board_id):
    
    for board in all_boards:
        if board["ID"] == board_id:
            return render_template("board.html", board=board)
    abort(404)

@app.route("/book", methods=["GET", "POST"])
def board_booking():
    
    if request.method == "POST":
        size = request.form["board_size"]
        return f"<h3>Board size {size} booked.</h3>"
    
    return render_template("book.html")

@app.route("/hours")
def hours():
    return "No hours yet"

# main
if __name__ == "__main__": 
    app.run(debug=True)