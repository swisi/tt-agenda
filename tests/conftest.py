import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def app(tmp_path):
    db_path = tmp_path / 'test.db'

    class TestConfig:
        TESTING = True
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = 'test-secret-key'
        WEBHOOK_ENABLED = False
        LOG_LEVEL = 'DEBUG'
        AUTO_CREATE_DB = False
        CREATE_DEFAULT_USERS = False

    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def csrf_token(client):
    def _csrf_token(path='/login'):
        client.get(path)
        with client.session_transaction() as sess:
            return sess['_csrf_token']
    return _csrf_token

@pytest.fixture
def create_user(app):
    def _create_user(username='test', password='test', role='user'):
        with app.app_context():
            user = User(username=username, role=role)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user
    return _create_user

@pytest.fixture
def login_as(client, create_user, csrf_token):
    def _login_as(username='test', password='test', role='user'):
        create_user(username=username, password=password, role=role)
        token = csrf_token('/login')
        response = client.post('/login', data={
            'username': username,
            'password': password,
            'csrf_token': token
        })
        return response
    return _login_as
