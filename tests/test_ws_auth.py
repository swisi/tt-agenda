import json
import pytest
from fastapi.testclient import TestClient

from tt_agenda_v2 import create_app
from tt_agenda_v2.config import Config as BaseConfig


def test_ws_auth_rejects_without_token():
    class Cfg(BaseConfig):
        TESTING = True
        WS_AUTH_TOKEN = "tok123"

    app = create_app(Cfg)
    client = TestClient(app)
    with pytest.raises(Exception):
        with client.websocket_connect('/ws/live'):
            pass


def test_ws_auth_accepts_with_query_token():
    class Cfg(BaseConfig):
        TESTING = True
        WS_AUTH_TOKEN = "tok456"

    app = create_app(Cfg)
    client = TestClient(app)
    with client.websocket_connect(f'/ws/live?token={Cfg.WS_AUTH_TOKEN}') as ws:
        msg = ws.receive_text()
        data = json.loads(msg)
        assert data.get('ok') is True


def test_ws_auth_accepts_with_header():
    class Cfg(BaseConfig):
        TESTING = True
        WS_AUTH_TOKEN = "tok789"

    app = create_app(Cfg)
    client = TestClient(app)
    headers = {'x-ws-token': Cfg.WS_AUTH_TOKEN}
    with client.websocket_connect('/ws/live', headers=headers) as ws:
        msg = ws.receive_text()
        data = json.loads(msg)
        assert data.get('ok') is True
