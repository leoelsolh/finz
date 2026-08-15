# Test Enviornment
import time
import datetime
import pytest

import db
import config
from main import app
from main import login_attempts

CSRF = 'test_token'

@pytest.fixture
def client():
    login_attempts.clear()
    with app.test_client() as client:
        with client.session_transaction() as sesh:
            sesh['csrf_token'] = CSRF
        yield client

# Test page-loads
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

def test_contact_loads(client):
    load = client.get('/contact')
    assert load.status_code == 200

def test_ourwork_loads(client):
    load = client.get('/ourwork')
    assert load.status_code == 200

def test_about_loads(client):
    load = client.get('/about')
    assert load.status_code == 200

# Test site functions
def test_login_lockout(client):
    for _ in range(4):
        invalid_response = client.post('/admin/login', data={'username': 'carl', 'password': 'wrong', 'csrf_token': CSRF})
        assert invalid_response.status_code == 401
    blocked = client.post('/admin/login', data={'username': 'carl', 'password': 'wrong', 'csrf_token': CSRF})
    assert blocked.status_code == 429

def test_failed_login(client):
    invalid_response = client.post('/admin/login', data={'username': 'carl', 'password': 'wrong', 'csrf_token': CSRF})
    assert invalid_response.status_code == 401

def test_successful_login(client):
    response = client.post('/admin/login', data={'username': config.ADMIN_USER, 'password': config.ADMIN_PASSWORD, 'csrf_token': CSRF}) 
    assert response.status_code == 302

    response = client.get('/admin')
    assert response.status_code == 200

def test_expired_session(client, monkeypatch):
    monkeypatch.setattr(app, 'permanent_session_lifetime', datetime.timedelta(seconds=1))

    response = client.post('/admin/login', data={'username': config.ADMIN_USER, 'password': config.ADMIN_PASSWORD, 'csrf_token': CSRF})
    assert response.status_code == 302 
    
    response = client.get('/admin')
    assert response.status_code == 200

    time.sleep(2)

    response = client.get('/admin')
    assert response.status_code == 302 

def test_oversized_post_rejection(client):
    payload = 'a' * 20000
    rejection = client.post('/book', data={'name': payload, 'csrf_token': CSRF})
    assert rejection.status_code == 413
    
def test_csrf_rejection(client):
    rejection = client.post('/admin/login', data={'username': 'x', 'password': 'y'})
    assert rejection.status_code == 403

def test_available_boards_counts_quantity(init_test_db):
    available = db.get_available_boards()
    assert available[0]['available'] == 11

def test_available_boards_count_drops(init_test_db):
    board_id = init_test_db #This will return the last row's board_id so we can use it in the test.
    db.mark_board_out(board_id, 'testxx')
    assert db.get_available_boards()[0]['available'] == 10

def test_available_boards_count_rises(init_test_db):
    board_id = init_test_db
    rental_ids = []

    for _ in range(3):
        rental_id = db.mark_board_out(board_id, 'test')
        rental_ids.append(rental_id)

    db.mark_board_in(rental_ids[1])

    active = db.get_active_rentals()
    assert len(active) == 2
    assert db.get_available_boards()[0]['available'] == 9


# Test database functions
def test_db_connection():
    #TODO: write a connection test.
    pass