#!/usr/bin/python3
#
#         [ Database Migrator ]
#
# Migration script for database schema changes
import sqlite3
from db import DatabaseError
from config import DB_PATH

migrations = [
    (1, '''
        CREATE TABLE IF NOT EXISTS boards (
            id       INTEGER PRIMARY KEY,
            name     TEXT,
            size     TEXT,
            price    INTEGER,
            quantity  INTEGER,
            damage_count INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id       INTEGER PRIMARY KEY,
            name     TEXT,
            phone    TEXT,
            email    TEXT,
            wetsuit  INTEGER,
            hire_date  TEXT,
            size_requested TEXT
        );
        CREATE TABLE IF NOT EXISTS rentals (
            id          INTEGER PRIMARY KEY,
            board_id    INTEGER,
            name_booked TEXT,
            went_out    TEXT,
            came_back   TEXT,
            damage_note TEXT
        )
    '''),
    (2, '''
        ALTER TABLE boards ADD COLUMN archived INTEGER DEFAULT 0;
    '''),
    (3, '''
        ALTER TABLE boards ADD COLUMN category TEXT DEFAULT 'surfboard';
    '''),
    (4, '''
        ALTER TABLE rentals ADD COLUMN hire_group TEXT;
    '''),
    (5, '''
        ALTER TABLE bookings ADD COLUMN board_qty INTEGER DEFAULT 1;
        ALTER TABLE bookings ADD COLUMN fulfilled INTEGER DEFAULT 0;
    ''')
]

def run_migrations():
    try:
        with sqlite3.connect(DB_PATH) as database:
            cursor = database.cursor()

            cursor.execute('''PRAGMA user_version''')
            current = cursor.fetchone()[0]

            for version, sql in migrations:
                if version <= current:
                    continue 
                
                cursor.executescript(sql)
                cursor.execute(f'PRAGMA user_version = {version}')
                database.commit()

    except sqlite3.Error as error:
        raise DatabaseError('Could not set schema') from error
