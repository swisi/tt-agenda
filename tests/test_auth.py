def test_logout_requires_post(client):
    response = client.get('/logout')
    assert response.status_code == 405


def test_logout_clears_session(client, csrf_token):
    client.get('/login')
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['username'] = 'logout-user'
        sess['user_role'] = 'user'
    logout_token = csrf_token('/')
    logout_response = client.post('/logout', data={'csrf_token': logout_token})
    assert logout_response.status_code == 302

    with client.session_transaction() as sess:
        assert 'user_id' not in sess
        assert 'username' not in sess
        assert 'user_role' not in sess
