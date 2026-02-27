from fastapi.testclient import TestClient
import pathlib
import sys


sys.path.insert(0, str(pathlib.Path("src").resolve()))
from tt_agenda_v2 import create_app


def test_root_renders():
    app = create_app()
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
    assert "Live-Ansicht" in r.text


def test_static_assets():
    app = create_app()
    client = TestClient(app)
    r_js = client.get("/static/js/live.js")
    r_css = client.get("/static/css/live.css")
    assert r_js.status_code == 200
    assert r_css.status_code == 200
