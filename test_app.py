# Test Enviornment
from main import app
client = app.test_client()

# Test page loads
def test_board_loads():
    response = client.get("/boards")
    assert response.status_code == 200

def test_admin_redirects():
    response = client.get("/admin")
    assert response.status_code == 302
    assert "/admin/login" in response.headers["Location"] 

def test_login_loads():
    response = client.get("/admin/login")
    assert response.status_code == 200

def test_book_loads():
    response = client.get("/book")
    assert response.status_code == 200

def test_index_loads():
    response = client.get("/")
    assert response.status_code == 200

# Test database connection
def test_db_connection():
    #TODO: Write a database test.
    pass