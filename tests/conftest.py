import pytest
from fastapi.testclient import TestClient

from tt_agenda_v2 import create_app


@pytest.fixture
def app(tmp_path):
    db_path = tmp_path / "test-v2.db"

    class TestConfig:
        TESTING = True
        SECRET_KEY = "test-secret"
        DATABASE_URL = f"sqlite:///{db_path}"
        AUTO_CREATE_DB = True
        CREATE_DEFAULT_USERS = True
        CREATE_DEFAULT_POSITIONS = True
        DEFAULT_ADMIN_USERNAME = "admin"
        DEFAULT_ADMIN_PASSWORD = "admin"
        DEFAULT_COACH_USERNAME = "coach"
        DEFAULT_COACH_PASSWORD = "coach"

    return create_app(TestConfig)


@pytest.fixture
def client(app):
    return TestClient(app)
