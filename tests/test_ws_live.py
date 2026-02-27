import pathlib
import sys
import json
from fastapi.testclient import TestClient

sys.path.insert(0, str(pathlib.Path("src").resolve()))
from tt_agenda_v2 import create_app


def test_ws_live_accepts_connection():
    app = create_app()
    client = TestClient(app)
    with client.websocket_connect('/ws/live') as ws:
        msg = ws.receive_text()
        data = json.loads(msg)
        assert data.get('ok') is True
        assert 'items' in data
