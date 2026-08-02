#!/usr/bin/python3
import os
from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.environ.get('DB_PATH', 'rental.db')
SHOP_TIMEZONE = 'Europe/London'

SECRET_KEY = os.environ['SECRET_KEY'] #Load signing key
ADMIN_HASH = os.environ['ADMIN_HASH'] #Load admin hash
ADMIN_USER = os.environ['ADMIN_USER'] #Load admin user
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD')

SESSION_LIFETIME_HOURS = 8
SESSION_COOKIE_SAMESITE = 'Lax'
#SESSION_COOKIE_SECURE = True
LOGIN_WINDOW_SECONDS = 3600
MAX_LOGIN_ATTEMPTS = 5