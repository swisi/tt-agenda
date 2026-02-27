import pathlib
import sys
import json
from fastapi.testclient import TestClient

sys.path.insert(0, str(pathlib.Path("src").resolve()))
from tt_agenda_v2 import create_app


def create_sample_template(client: TestClient):
    payload = {
        "name": "T1",
        "valid_from": "2026-01-01",
        "valid_to": "2026-12-31",
        "weekday": 0,
        "start_time": "10:00",
        "is_active": True,
        "activities": [],
    }
    r = client.post("/api/v1/templates", json=payload)
    assert r.status_code == 201
    return r.json()["id"] if isinstance(r.json(), dict) and "id" in r.json() else r.json().get("id")


def test_template_edit_post():
    app = create_app()
    client = TestClient(app)
    # login as admin for UI edit
    rlogin = client.post('/login', data={'username': 'admin', 'password': 'admin'})
    assert rlogin.status_code in (302, 303, 307)
    client.cookies.set('session', rlogin.cookies.get('session'))
    tid = create_sample_template(client)

    # GET edit page
    r = client.get(f"/templates/{tid}/edit")
    assert r.status_code == 200

    # POST changes
    form = {"name": "T1-updated", "weekday": "2", "start_time": "11:15", "is_active": "on"}
    r2 = client.post(f"/templates/{tid}/edit", data=form)
    # TestClient will follow redirect; ensure final response is OK
    assert r2.status_code == 200 or r2.status_code in (302, 303)

    # Verify via API
    r3 = client.get(f"/api/v1/templates")
    assert r3.status_code == 200
    items = r3.json()
    assert any(t["id"] == tid and t["name"] == "T1-updated" for t in items)
