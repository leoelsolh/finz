#!/usr/bin/env bash
set -e
if [ ! -f 'rental.db' ]; then
    python3 seed.py
    echo 'Seeding complete' 
fi

python3 main.py 