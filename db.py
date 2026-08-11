#!/usr/bin/python3
import datetime
import sqlite3
import contextlib
import logging
from zoneinfo import ZoneInfo

import config

class DatabaseError(Exception):
    '''Raised when a database operation fails.'''

@contextlib.contextmanager
def get_connection():
    connection = sqlite3.connect(config.DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
    finally:
        connection.close()

# Site helpers
def get_board_types():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''
                SELECT name, size, price, COUNT(*) AS quantity
                FROM boards
                GROUP BY name, size, price
            ''')
    
    except sqlite3.OperationalError as op_error:
        logging.exception('Failed to group boards')
        raise DatabaseError('Could not group boards') from op_error

def get_board_sizes():
    try: 
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''SELECT DISTINCT size FROM boards''')
            return cursor.fetchall()

    except sqlite3.OperationalError as op_error:
        logging.exception('Failed to fetch boards by size')
        raise DatabaseError('Could not fetch boards by size') from op_error

def add_booking(name, phone, email, wetsuit, hire_date, size):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''
                INSERT INTO bookings (name, phone, email, wetsuit, hire_date, size_requested) VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, phone, email, wetsuit, hire_date, size))

            connection.commit()

    except sqlite3.Error as error:
        logging.exception('Failed to add booking')
        raise DatabaseError('Could not save booking') from error

def get_available_boards():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''
                SELECT * FROM (
                    SELECT id, name, size, price, 
                        quantity - damage_count - (
                            SELECT COUNT(*) FROM rentals
                            WHERE rentals.board_id = boards.id
                            AND came_back IS NULL
                        ) AS available
                    FROM boards
                ) WHERE available > 0
            ''')
            return cursor.fetchall()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to fetch available boards')
        raise DatabaseError('Could not fetch available boards') from sql_error


# Admin logic
def mark_board_out(board_id, renter_name):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            
            went_out = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO rentals (went_out, board_id, name_booked) VALUES (?, ?, ?)
            ''', (went_out, board_id, renter_name))
            
            connection.commit()
    
    except sqlite3.Error as sql_error:
        logging.exception('Failed to mark board out')
        raise DatabaseError('Could not mark board out') from sql_error

def mark_board_in(rental_id, damaged=0, damage_note=None):
    try:
        with get_connection() as connection:
            cursor = connection.cursor() 

            if not damage_note: 
                damage_note = None 

            else: 
                damage_note = damage_note.strip()
                if not damage_note:
                    damage_note = None

            cursor.execute('''
                SELECT board_id
                FROM rentals 
                WHERE id = ?            
            ''', (rental_id,))

            rental_row = cursor.fetchone()

            if not rental_row:
                return

            came_back = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE rentals SET came_back = ?, damage_note = ?
                WHERE id = ? AND came_back IS NULL
            ''', (came_back, damage_note, rental_id))

            if damaged:
                cursor.execute('''
                    UPDATE boards SET damage_count = damage_count + 1 WHERE id = ?
                ''', (rental_row['board_id'],))

            connection.commit()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to mark board in')
        raise DatabaseError('Could not mark board in') from sql_error

def get_active_rentals():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''
                SELECT boards.id AS board_id, boards.name, boards.size, rentals.name_booked, rentals.went_out, rentals.id AS rental_id
                FROM rentals
                JOIN boards ON rentals.board_id = boards.id
                WHERE came_back IS NULL
            ''')
            return cursor.fetchall()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to fetch active rentals')
        raise DatabaseError('Could not fetch active rentals') from sql_error

def get_todays_bookings():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            today = datetime.datetime.now(ZoneInfo(config.SHOP_TIMEZONE)).strftime('%Y-%m-%d')
            cursor.execute('''SELECT * FROM bookings WHERE hire_date = ?''', (today,))
            return cursor.fetchall()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to get todays bookings')
        raise DatabaseError('Could not get todays bookings') from sql_error

