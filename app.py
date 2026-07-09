#!/usr/bin/python3
from flask import Flask, render_template, abort

app = Flask(__name__)

# database
all_boards = [
    {"ID": 1, "name": "Swirl", "size": "8'0", "price": 50},
    {"ID": 2, "name": "Hardboard", "size": "6'5", "price": 80},
    {"ID": 3, "name": "Oz", "size": "9'0", "price": 60},
    {"ID": 4, "name": "Max", "size": "9'0", "price": 60},
]

# Site routes
@app.route("/")
def index():
    return "Hi Browser"


@app.route("/boards")
def boards():
    return render_template("boards.html", boards=all_boards) 


@app.route("/boards/<int:board_id>")
def show_board(board_id):
    
    for board in all_boards:
        if board["ID"] == board_id:
            return render_template("board.html", board=board)
    abort(404)

@app.route("/hours")
def hours():
    return "No hours yet"

# main
if __name__ == "__main__": 
    app.run(debug=True)