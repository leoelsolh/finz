#!/usr/bin/env bash
import schema
schema.init_db()

rm rental.db 
python3 seed.py

echo "Seeding complete"