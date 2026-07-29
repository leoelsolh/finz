#!/usr/bin/python3
import os 
import pytest
import sqlite3

os.environ['DB_PATH'] = 'test_rental.db'

@pytest.fixture
def init_test_db():
    try:
        with sqlite3.connect(os.environ['DB_PATH']) as database:
            cursor = database.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS boards (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    size TEXT,
                    price INTEGER
                )
            ''')
            board = [("RYD", "8'0", 25)]
            cursor.executemany('''INSERT INTO boards (name, size, price) VALUES (?, ?, ?)''', board)
    
    except sqlite3.Error as error:
        print(f"\n[ Seeding of Test-Database Failed ]:\n{error}\n")