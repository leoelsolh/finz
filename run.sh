#!/usr/bin/env bash
set -e
if [ ! -f 'rental.db' ]; then
    python3 seed.py
    echo 'Seeding complete' 
fi

gunicorn --bind 127.0.0.1:5000 --workers 1 main:app