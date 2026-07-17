#!/usr/bin/env bash

#TODO: 
# Make this script into a runtime script,
# that checks if rental.db has been seeded
# if not, it seeds the db. Otherwise it 
# skips straight to running the app. 

rm -f rental.db 
python3 seed.py
echo "Seeding complete"