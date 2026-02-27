from fastapi.testclient import TestClient
from tt_agenda_v2 import create_app


def test_login_form_sets_cookie():
    app = create_app()
    client = TestClient(app)

    # GET login page
    r = client.get('/login')
    assert r.status_code == 200

    # POST login with default seeded admin credentials
    r = client.post('/login', data={'username': 'admin', 'password': 'admin'})
    # should redirect
    assert r.status_code in (303, 307, 302)
    # cookie set
    assert 'session' in r.cookies

    # access root with cookie
    client.cookies.set('session', r.cookies.get('session'))
    r2 = client.get('/')
    assert r2.status_code == 200
