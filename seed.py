#!/usr/bin/python3
#
#         [ Seed Script ]
# 
# This script seeds the database with 
# placeholder data for development and 
# testing purposes. None of the data is 
# real or used in prod.

import sqlite3
import datetime
import config
import schema
schema.run_migrations()

try:
    with sqlite3.connect(config.DB_PATH) as database:
        cursor = database.cursor()
        boards = [
            ("Ryd", "8'0", 25, 14),
            ("Tidal", "8'0", 25, 4),
            ("Ryd", "9'0", 25, 8),
            ("Tidal", "9'0", 25, 3),
            ("Oz", "9'0", 25, 1),
        ]
            
        
        cursor.executemany('''INSERT INTO boards (name, size, price, quantity) VALUES (?, ?, ?, ?)''', boards)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        bookings = [
            ("Sophie Reece", "07700 900111", "sophie@example.com", 1, today, "8'0"),
            ("Tom Bevan", "07700 900222", "tom@example.com", 0, today, "6'5"),
        ]
        cursor.executemany('''INSERT INTO bookings (name, phone, email, wetsuit, hire_date, size_requested) VALUES (?, ?, ?, ?, ?, ?)''', bookings)

        
except sqlite3.Error as error:
    print(f"Seeding failed: {error}") 