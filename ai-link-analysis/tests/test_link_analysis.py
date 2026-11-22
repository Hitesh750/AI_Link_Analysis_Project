from fastapi.testclient import TestClient

from app.main import app
from app.utils.validators import validate_public_url
from fastapi import HTTPException

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_rejects_non_http_scheme():
    try:
        validate_public_url("file:///etc/passwd")
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 400


def test_rejects_localhost():
    try:
        validate_public_url("http://localhost:8000")
        assert False, "Expected HTTPException"
    except HTTPException as exc:
        assert exc.status_code == 400
