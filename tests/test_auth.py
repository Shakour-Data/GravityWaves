import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, User

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def register(client, username, email, password, confirm_password):
    return client.post('/register', data={
        'username': username,
        'email': email,
        'password': password,
        'confirm_password': confirm_password
    }, follow_redirects=True)

def login(client, username, password):
    return client.post('/login', data={
        'username': username,
        'password': password
    }, follow_redirects=True)

def test_successful_registration(client):
    rv = register(client, 'testuser', 'test@example.com', 'password123', 'password123')
    assert b'Create a New Account' not in rv.data  # Should redirect away from register page
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.email == 'test@example.com'

def test_registration_missing_fields(client):
    rv = register(client, '', 'test@example.com', 'password123', 'password123')
    assert b'Please fill in all fields' in rv.data

    rv = register(client, 'testuser', '', 'password123', 'password123')
    assert b'Please fill in all fields' in rv.data

    rv = register(client, 'testuser', 'test@example.com', '', 'password123')
    assert b'Please fill in all fields' in rv.data

    rv = register(client, 'testuser', 'test@example.com', 'password123', '')
    assert b'Please fill in all fields' in rv.data

def test_registration_password_mismatch(client):
    rv = register(client, 'testuser', 'test@example.com', 'password123', 'password321')
    assert b'Passwords do not match' in rv.data

def test_registration_duplicate_username(client):
    register(client, 'testuser', 'test1@example.com', 'password123', 'password123')
    rv = register(client, 'testuser', 'test2@example.com', 'password123', 'password123')
    assert b'Username already exists' in rv.data

def test_registration_duplicate_email(client):
    register(client, 'testuser1', 'test@example.com', 'password123', 'password123')
    rv = register(client, 'testuser2', 'test@example.com', 'password123', 'password123')
    assert b'Email already registered' in rv.data

def test_successful_login(client):
    register(client, 'testuser', 'test@example.com', 'password123', 'password123')
    rv = login(client, 'testuser', 'password123')
    assert b'Invalid username or password' not in rv.data
    assert b'Create a New Account' not in rv.data  # Should redirect away from login page

def test_login_invalid_credentials(client):
    register(client, 'testuser', 'test@example.com', 'password123', 'password123')
    rv = login(client, 'testuser', 'wrongpassword')
    assert b'Invalid username or password' in rv.data

def test_login_missing_fields(client):
    rv = login(client, '', 'password123')
    assert b'Username and password are required' in rv.data or b'Invalid username or password' in rv.data

    rv = login(client, 'testuser', '')
    assert b'Username and password are required' in rv.data or b'Invalid username or password' in rv.data
