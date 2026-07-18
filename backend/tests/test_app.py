from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_openapi_available():
    resp = client.get("/api/v1/openapi.json")
    assert resp.status_code == 200
    schema = resp.json()
    assert schema["info"]["title"]
    assert "/api/v1/auth/login" in schema["paths"]


def test_protected_route_requires_auth():
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401
