def test_health_live(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_health_ready(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ready"
