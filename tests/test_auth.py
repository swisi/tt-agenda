def test_login_with_default_admin(client):
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "admin"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["role"] == "admin"


def test_login_with_default_user(client):
    response = client.post(
        "/auth/login",
        json={"username": "user", "password": "user"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload["role"] == "user"


def test_login_with_wrong_password(client):
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.get_json()["ok"] is False
