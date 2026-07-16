#!/usr/bin/env bash
rm -f rental.db 
python3 seed.py
echo "Seeding complete"