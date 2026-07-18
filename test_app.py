# Test Enviornment
import os
import pytest
from main import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# Test page loads
def test_board_loads(client):
    response = client.get('/boards')
    assert response.status_code == 200

def test_admin_redirects(client):
    response = client.get('/admin')
    assert response.status_code == 302
    assert '/admin/login' in response.headers['Location'] 

def test_login_loads(client):
    response = client.get('/admin/login')
    assert response.status_code == 200

def test_book_loads(client):
    response = client.get('/book')
    assert response.status_code == 200

def test_index_loads(client):
    response = client.get('/')
    assert response.status_code == 200

# Test site functions
def test_failed_login(client):
    response = client.post('/admin/login', data={'username': 'carl', 'password': 'wrong'})
    assert response.status_code == 404

def test_successfull_login(client):
    response = client.post('/admin/login', data={'username': os.environ['ADMIN_USER'], 'password': os.environ['ADMIN_PASSWORD']}) 
    assert response.status_code == 302

# Test database connection
#TODO: Write a database test.