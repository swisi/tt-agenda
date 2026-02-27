import pathlib
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, str(pathlib.Path("src").resolve()))
from tt_agenda_v2 import create_app


def test_templates_page_renders():
    app = create_app()
    client = TestClient(app)
    # login first
    r1 = client.post('/login', data={'username': 'admin', 'password': 'admin'})
    assert r1.status_code in (302, 303, 307)
    client.cookies.set('session', r1.cookies.get('session'))
    r = client.get('/templates')
    # page should render even if no templates in DB
    assert r.status_code == 200
    assert 'Trainingsvorlagen' in r.text
