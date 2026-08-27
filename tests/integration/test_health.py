from unittest.mock import patch


def test_health_returns_ok(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "cpl"


def test_ready_with_db_available(test_client):
    with patch("app.db.engine.check_db_connection", return_value=True):
        response = test_client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["application"] == "ready"
        assert data["database"] == "reachable"


def test_ready_without_db_returns_503(test_client):
    with patch("app.db.engine.check_db_connection", return_value=False):
        response = test_client.get("/ready")
        assert response.status_code == 503
        data = response.json()
        assert data["database"] == "unreachable"
