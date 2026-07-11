#!/usr/bin/python3
# test.py  /  not prod.
import sqlite3

try:
    with sqlite3.connect("test.db") as connection:
        cursor = connection.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS boards (
                id   INTEGER PRIMARY KEY,
                name TEXT,
                size TEXT
            )
        ''')

except sqlite3.Error as error:
    print(f"Cant fetch boards: {error}")

# Insert Data
def insert_to_db():
    with sqlite3.connect("test.db") as connection:
        cursor = connection.cursor()

        cursor.execute('''INSERT INTO boards (name, size) VALUES (?, ?)''', ("Swell", "8'0"))

def get_board_by_id(board_id):
    try:
        connection = sqlite3.connect("test.db")
        cursor = connection.cursor()

        cursor.execute('''SELECT * FROM boards WHERE id = ?''', (board_id,))
        
        return cursor.fetchone()

    except sqlite3.OperationalError as operation_error:
        return f"Error in this operation: {operation_error}"
    
# main 
insert_to_db()
get_board_by_id(5)


#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#

