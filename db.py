#!/usr/bin/python3
#
#       [ Database Helpers ]
#
# Sqlite3 python queries, served to the 
# main script to seperate database operations
# from frontend route logic

import datetime
import sqlite3
import contextlib
import logging
import secrets
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
def get_board_sizes():
    try: 
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''

                SELECT DISTINCT size 
                FROM boards
                WHERE archived = 0

            ''')
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
                    SELECT id, name, size, price, category, 
                        quantity - damage_count - (
                            SELECT COUNT(*) FROM rentals
                            WHERE rentals.board_id = boards.id
                            AND came_back IS NULL
                        ) AS available
                    FROM boards WHERE archived = 0
                ) WHERE available > 0

            ''')
            return cursor.fetchall()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to fetch available boards')
        raise DatabaseError('Could not fetch available boards') from sql_error

# Admin logic
def add_new_board(name, size, price, quantity, category):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''

                INSERT INTO boards (name, size, price, quantity, category)
                VALUES (?, ?, ?, ?, ?)

            ''', (name, size, price, quantity, category))

            connection.commit()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to add new board')
        raise DatabaseError('Could not add new board.') from sql_error

def mark_board_out(board_id, renter_name):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            
            went_out = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''

                INSERT INTO rentals (went_out, board_id, name_booked) VALUES (?, ?, ?)

            ''', (went_out, board_id, renter_name))
            
            connection.commit()
            
            rental_id = cursor.lastrowid
            return rental_id

    except sqlite3.Error as sql_error:
        logging.exception('Failed to mark board out')
        raise DatabaseError('Could not mark board out') from sql_error

def mark_hire_out(board_ids, renter_name):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            hire_group = secrets.token_hex(8) 
            went_out = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            
            for board_id in board_ids:
                cursor.execute('''

                    INSERT INTO rentals (went_out, board_id, name_booked, hire_group) VALUES (?, ?, ?, ?)
                
                ''', (went_out, board_id, renter_name, hire_group))

            connection.commit()
            
    except sqlite3.Error as sql_error:
        logging.exception('Failed to mark rental out')
        raise DatabaseError('Could not mark rental out') from sql_error

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

                UPDATE rentals 
                SET came_back = ?, damage_note = ?
                WHERE id = ? 
                AND came_back IS NULL

            ''', (came_back, damage_note, rental_id))

            row_count = cursor.rowcount
            if row_count == 0:
                return

            if damaged:
                cursor.execute('''

                    UPDATE boards 
                    SET damage_count = damage_count + 1 
                    WHERE id = ?

                ''', (rental_row['board_id'],))

            connection.commit()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to mark board in')
        raise DatabaseError('Could not mark board in.') from sql_error

def get_all_boards():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('''

                SELECT id, name, size, price, quantity
                FROM boards
                WHERE archived = 0
                ORDER BY name

            ''')
            return cursor.fetchall()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to get all boards')
        raise DatabaseError('Could not fetch all boards.') from sql_error

def get_damaged_boards():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''

                SELECT id, name, size, damage_count
                FROM boards
                WHERE damage_count > 0

            ''')
            return cursor.fetchall()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to fetch damaged boards')
        raise DatabaseError('Could not fetch damaged boards.') from sql_error

def clear_damage_from_board(board_id):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''

                UPDATE boards 
                SET damage_count = damage_count - 1 
                WHERE damage_count > 0
                AND id = ?

            ''', (board_id,))

            connection.commit()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to clear damage-marker from board.')
        raise DatabaseError('Could not clear damage-marker from board.') from sql_error

def archive_board(board_id):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''

                UPDATE boards
                SET archived = 1
                WHERE id = ?

            ''', (board_id,))

            connection.commit()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to archive board')
        raise DatabaseError('Could not archive this board.') from sql_error

def set_board_quantity(quantity, board_id):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''

                UPDATE boards 
                SET quantity = ?
                WHERE id = ?

            ''', (quantity, board_id))

            connection.commit()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to set board quantity')
        raise DatabaseError('Could not update board quantity') from sql_error

def get_active_rentals(search=None):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            if search:
                like = f'%{search}%'
                cursor.execute('''

                    SELECT boards.id AS board_id, boards.name, boards.size, boards.category, rentals.hire_group, rentals.name_booked, rentals.went_out, rentals.id AS rental_id
                    FROM rentals
                    JOIN boards ON rentals.board_id = boards.id
                    WHERE came_back IS NULL

                    AND name_booked LIKE ?
                    ORDER BY rentals.hire_group

                ''', (like,))
                return cursor.fetchall()

            else:
                cursor.execute('''

                    SELECT boards.id AS board_id, boards.name, boards.size, boards.category, rentals.hire_group, rentals.name_booked, rentals.went_out, rentals.id AS rental_id
                    FROM rentals
                    JOIN boards ON rentals.board_id = boards.id
                    WHERE came_back IS NULL
                    ORDER BY rentals.hire_group

                ''')
                return cursor.fetchall()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to fetch active rentals')
        raise DatabaseError('Could not fetch active rentals.') from sql_error

def get_income_since(cutoff):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('''

                SELECT COALESCE(SUM(boards.price), 0)
                FROM rentals
                JOIN boards ON rentals.board_id = boards.id
                WHERE rentals.went_out >= ?

            ''', (cutoff,))
            return cursor.fetchone()[0]

    except sqlite3.Error as sql_error:
        logging.exception('Failed to fetch net-income')
        raise DatabaseError('Could not fetch net-income') from sql_error

def get_bookings_count_since(cutoff):
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            cursor.execute('''
            
                SELECT COUNT(*)
                FROM bookings
                WHERE hire_date >= ?

            ''', (cutoff,))
            return cursor.fetchone()[0]

    except sqlite3.Error as sql_error:
        logging.exception('Failed to get bookings count')
        raise DatabaseError('Could not get bookings count') from sql_error

def get_hires_per_day_since(cutoff):
    try: 
        with get_connection() as connection: 
            cursor = connection.cursor()

            cursor.execute('''
            
                SELECT DATE(rentals.went_out) AS DAY, COUNT(*) AS hires
                FROM rentals
                WHERE rentals.went_out >= ? 
                GROUP BY day 
                ORDER BY day
            
            ''', (cutoff,))
            return cursor.fetchall()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to get hires-per-day statistics')
        raise DatabaseError('Could not get hires-per-day statistics') from sql_error

def get_todays_bookings():
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            today = datetime.datetime.now(ZoneInfo(config.SHOP_TIMEZONE)).strftime('%Y-%m-%d')
            cursor.execute('''
            
                SELECT * 
                FROM bookings 
                WHERE hire_date = ?
                
            ''', (today,))
            return cursor.fetchall()

    except sqlite3.Error as sql_error:
        logging.exception('Failed to get todays bookings')
        raise DatabaseError('Could not get todays bookings') from sql_error

