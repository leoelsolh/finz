#!/usr/bin/env bash
rm rental.db 
python3 main.py
python3 seed.py

echo("Seeding complete")