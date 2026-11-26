from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app


def _unavailable_client():
    patches = (
        patch("app.predictor.load", side_effect=FileNotFoundError("synthetic missing bundle")),
        patch("app.predictor.loaded", False),
        patch("app.preprocess"),
        patch("app.distilbert_predictor.load", side_effect=FileNotFoundError("synthetic missing deep model")),
    )
    return patches


def test_security_headers_apply_to_ui_and_operational_responses():
    with _unavailable_client()[0], _unavailable_client()[1], _unavailable_client()[2], _unavailable_client()[3]:
        with TestClient(app) as client:
            for path in ("/", "/health", "/docs", "/openapi.json"):
                response = client.get(path)
                assert response.headers["X-Content-Type-Options"] == "nosniff"
                assert response.headers["X-Frame-Options"] == "DENY"
                assert response.headers["Referrer-Policy"] == "no-referrer"
                assert response.headers["Permissions-Policy"] == "camera=(), microphone=(), geolocation=()"


def test_metrics_is_not_public_without_explicit_access_configuration():
    with _unavailable_client()[0], _unavailable_client()[1], _unavailable_client()[2], _unavailable_client()[3], \
         patch("routers.api.METRICS_ACCESS_TOKEN", None):
        with TestClient(app) as client:
            response = client.get("/metrics")

    assert response.status_code == 404
    assert "total_requests" not in response.text


def test_metrics_requires_bearer_token_when_configured():
    with _unavailable_client()[0], _unavailable_client()[1], _unavailable_client()[2], _unavailable_client()[3], \
         patch("routers.api.METRICS_ACCESS_TOKEN", "synthetic-metrics-token"):
        with TestClient(app) as client:
            missing = client.get("/metrics")
            wrong = client.get("/metrics", headers={"Authorization": "Bearer wrong-token"})
            allowed = client.get("/metrics", headers={"Authorization": "Bearer synthetic-metrics-token"})

    assert missing.status_code == 401
    assert wrong.status_code == 401
    assert allowed.status_code == 200
    assert allowed.json()["models_loaded"] is False
