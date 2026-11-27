from unittest.mock import patch

from fastapi.testclient import TestClient

from app import app
from artifact_contract import ArtifactVerificationError


def test_health_is_not_ready_when_models_are_unavailable():
    with patch("app.predictor.load"), patch("app.predictor.loaded", False):
        with TestClient(app) as client:
            response = client.get("/health")
            assert response.status_code == 503
            assert response.json()["status"] == "not_ready"
            assert response.json()["models_loaded"] is False


def test_inference_is_rejected_when_models_are_unavailable():
    with patch("app.predictor.load"), patch("app.predictor.loaded", False):
        with TestClient(app) as client:
            response = client.post(
                "/analyze",
                json={"title": "A title", "text": "This is a sufficiently long article body for testing."},
            )
            assert response.status_code == 503


def test_startup_integrity_failure_keeps_application_available_but_not_ready():
    with patch("app.predictor.load", side_effect=ArtifactVerificationError("invalid bundle")):
        with TestClient(app) as client:
            response = client.get("/health")

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["models_loaded"] is False
