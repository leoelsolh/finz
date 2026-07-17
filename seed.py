#!/usr/bin/python3
# Seed Script
import sqlite3
import datetime
import schema
schema.init_db()

try:
    with sqlite3.connect("rental.db") as database:
        cursor = database.cursor()
        boards = [
            ("Swirl", "8'0", 50),
            ("Hardboard", "6'5", 80),
            ("Oz", "9'0", 60),
            ("Max", "9'0", 60),
        ]
        cursor.executemany('''INSERT INTO boards (name, size, price) VALUES (?, ?, ?)''', boards)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        bookings = [
            ("Sophie Reece", "07700 900111", "sophie@example.com", 1, today, "8'0"),
            ("Tom Bevan", "07700 900222", "tom@example.com", 0, today, "6'5"),
        ]
        cursor.executemany('''INSERT INTO bookings (name, phone, email, wetsuit, hire_date, size_requested) VALUES (?, ?, ?, ?, ?, ?)''', bookings)

        
except sqlite3.Error as error:
    print(f"Seeding failed: {error}")