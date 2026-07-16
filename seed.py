#!/usr/bin/python3
# Seed Script
import sqlite3
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
        
except sqlite3.Error as error:
    print(f"Seeding failed: {error}")