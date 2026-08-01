#!/usr/bin/python3
import sqlite3
from config import DB_PATH

def init_db():
    try:
        with sqlite3.connect(DB_PATH) as database:
            cursor = database.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS boards (
                    damaged INTEGER DEFAULT 0,
                    id     INTEGER PRIMARY KEY,
                    name   TEXT,
                    size   TEXT,
                    price  INTEGER
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
                    came_back   TEXT,
                    damage_note TEXT
                )
            ''')

    except sqlite3.Error as error:
        raise Exception(f"\nCant load database...\n{error}\n")
