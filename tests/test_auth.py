from app.models import User
from app.extensions import db


def test_logout_requires_post(client):
    response = client.get('/logout')
    assert response.status_code == 405


def test_logout_clears_session(client, app, csrf_token):
    with app.app_context():
        user = User(username='logout-user', role='user')
        user.set_password('secret')
        # Persist user for realistic login session
        db.session.add(user)
        db.session.commit()

    token = csrf_token('/login')
    login_response = client.post('/login', data={
        'username': 'logout-user',
        'password': 'secret',
        'csrf_token': token
    })
    assert login_response.status_code == 302

    logout_token = csrf_token('/')
    logout_response = client.post('/logout', data={'csrf_token': logout_token})
    assert logout_response.status_code == 302

    with client.session_transaction() as sess:
        assert 'user_id' not in sess
        assert 'username' not in sess
        assert 'user_role' not in sess
