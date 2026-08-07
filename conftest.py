#!/usr/bin/python3
import os 
import pytest
import sqlite3

os.environ['DB_PATH'] = 'test_rental.db'

@pytest.fixture
def init_test_db():
    with sqlite3.connect(os.environ['DB_PATH']) as database:
        cursor = database.cursor()

        cursor.execute('''DELETE FROM boards''')

        board = [("RYD", "8'0", 25, 11)]
        cursor.executemany(
            '''INSERT INTO boards (name, size, price, quantity) VALUES (?, ?, ?, ?)''',
            board
        )
        database.commit()