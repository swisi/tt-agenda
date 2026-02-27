def test_index_requires_login(client):
    response = client.get('/')
    assert response.status_code == 302  # Redirect to login

def test_test_route(client):
    response = client.get('/test')
    assert response.status_code == 200
    assert b'Flask funktioniert!' in response.data

def test_login(client, create_user, csrf_token):
    create_user(username='test', password='test', role='user')
    token = csrf_token('/login')
    response = client.post('/login', data={'username': 'test', 'password': 'test', 'csrf_token': token})
    assert response.status_code == 302  # Redirect after login

def test_login_requires_csrf(client, create_user):
    create_user(username='test', password='test', role='user')
    response = client.post('/login', data={'username': 'test', 'password': 'test'})
    assert response.status_code == 400
