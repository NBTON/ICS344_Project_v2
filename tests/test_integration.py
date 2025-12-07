import pytest
from backend.app import create_app
from backend.database import db, Users
import json

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_register_login(client):
    # Register
    res = client.post('/api/register', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert 'user_id' in data
    assert 'fingerprint' in data

    # Login
    res = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert res.status_code == 200

    # Login with wrong password
    res = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'wrongpassword'
    })
    assert res.status_code == 401

def test_message_flow(client):
    # Register User A
    client.post('/api/register', json={'username': 'alice', 'password': 'password123'})
    res_a = client.post('/api/login', json={'username': 'alice', 'password': 'password123'})
    # Cookie is handled by test_client automatically

    # Register User B
    # Need new client or logout? Test client persists cookies.
    # We can use separate clients or logout.

    # Let's use session trick or just get user B's ID from DB helper
    with client.application.app_context():
        user_a = Users.query.filter_by(username='alice').first()

    client.post('/api/logout')

    client.post('/api/register', json={'username': 'bob', 'password': 'password456'})
    client.post('/api/login', json={'username': 'bob', 'password': 'password456'})

    with client.application.app_context():
        user_b = Users.query.filter_by(username='bob').first()

    # Bob sends message to Alice
    res = client.post('/api/messages/send', json={
        'recipient_id': user_a.user_id,
        'content': 'Hello Alice'
    })
    assert res.status_code == 201

    client.post('/api/logout')

    # Alice logs in and checks messages
    client.post('/api/login', json={'username': 'alice', 'password': 'password123'})

    res = client.get(f'/api/messages/{user_b.user_id}')
    assert res.status_code == 200
    msgs = res.get_json()
    assert len(msgs) == 1
    assert msgs[0]['content'] == 'Hello Alice'
    assert msgs[0]['is_sender'] == False
