#!/usr/bin/python3
import os
from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.environ.get('DB_PATH', 'rental.db')

SHOP_TIMEZONE = 'Europe/London'

SECRET_KEY = os.environ['SECRET_KEY'] #Load signing key
ADMIN_HASH = os.environ['ADMIN_HASH'] #Load admin hash
ADMIN_USER = os.environ['ADMIN_USER'] #Load admin user
