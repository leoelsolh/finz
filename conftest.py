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
        cursor.execute('''DELETE FROM rentals''')
        cursor.execute(
            '''INSERT INTO boards (name, size, price, quantity) VALUES (?, ?, ?, ?)''',
            ("RYD", "8'0", 25, 11)
        )

        board_id = cursor.lastrowid
        database.commit()
        return board_id