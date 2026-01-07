import pytest
from app.models import User
from app.extensions import db

def test_index_requires_login(client):
    response = client.get('/')
    assert response.status_code == 302  # Redirect to login

def test_test_route(client):
    response = client.get('/test')
    assert response.status_code == 200
    assert b'Flask funktioniert!' in response.data

def test_login(client, app):
    with app.app_context():
        user = User(username='test', role='user')
        user.set_password('test')
        db.session.add(user)
        db.session.commit()

    response = client.post('/login', data={'username': 'test', 'password': 'test'})
    assert response.status_code == 302  # Redirect after login