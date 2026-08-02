# Test Enviornment
import os
import time
import datetime
import pytest

import config
from main import app
from main import login_attempts
from db import get_all_boards

@pytest.fixture
def client():
    login_attempts.clear()
    with app.test_client() as client:
        yield client

# Test page-loads
def test_board_loads(client):
    load = client.get('/boards')
    assert load.status_code == 200

def test_admin_redirects(client):
    load = client.get('/admin')
    assert load.status_code == 302
    assert '/admin/login' in load.headers['Location'] 

def test_login_loads(client):
    load = client.get('/admin/login')
    assert load.status_code == 200

def test_book_loads(client):
    load = client.get('/book')
    assert load.status_code == 200

def test_index_loads(client):
    load = client.get('/')
    assert load.status_code == 200


# Test site functions
def test_login_lockout(client):
    for _ in range(5):
        invalid_response = client.post('/admin/login', data={'username': 'carl', 'password': 'wrong'})
        assert invalid_response.status_code == 401
    blocked = client.post('/admin/login', data={'username': 'carl', 'password': 'wrong'})
    assert blocked.status_code == 429

def test_failed_login(client):
    invalid_response = client.post('/admin/login', data={'username': 'carl', 'password': 'wrong'})
    assert invalid_response.status_code == 401

def test_successful_login(client):
    response = client.post('/admin/login', data={'username': config.ADMIN_USER, 'password': config.(ADMIN_PASSWORD)}) 
    assert response.status_code == 302

    response = client.get('/admin')
    assert response.status_code == 200

def test_expired_session(client, monkeypatch):
    monkeypatch.setattr(app, 'permanent_session_lifetime', datetime.timedelta(seconds=1))

    response = client.post('/admin/login', data={'username': config.ADMIN_USER, 'password': config.ADMIN_PASSWORD})
    assert response.status_code == 302 
    
    response = client.get('/admin')
    assert response.status_code == 200

    time.sleep(2)

    response = client.get('/admin')
    assert response.status_code == 302 


# Test database functions
def test_db_connection():
    #TODO: write a connection test.
    pass

def test_get_all_boards(init_test_db):
    boards = get_all_boards()
    assert boards is not None
    assert len(boards) >= 1
    assert boards[0]['name'] is not None
