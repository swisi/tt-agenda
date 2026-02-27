import json
from fastapi.testclient import TestClient

from tt_agenda_v2 import create_app


def test_ws_receives_diff_on_adhoc_creation():
    app = create_app()
    client = TestClient(app)

    # connect websocket and receive initial snapshot
    with client.websocket_connect('/ws/live') as ws:
        msg = json.loads(ws.receive_text())
        assert msg.get('ok') is True

        # create adhoc instance for today via API
        today = __import__('datetime').date.today().isoformat()
        payload = {"name": "TmpAdhoc", "date": today, "start_time": "23:59", "activities": []}
        r = client.post('/api/v1/instances/adhoc', json=payload)
        assert r.status_code == 201

        # the server should broadcast a diff; read next message
        nxt = json.loads(ws.receive_text())
        assert nxt.get('ok') is True
        assert nxt.get('type') == 'diff'
        assert 'added' in nxt.get('diff', {})