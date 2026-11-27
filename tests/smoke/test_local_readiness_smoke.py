"""Model-free smoke tests for TruthScan's fail-closed local state.

These tests use the real FastAPI routes and served frontend, but patch every
startup path that could load a model or preprocessing resource. They never
perform real inference.
"""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app import app


@pytest.fixture
def unavailable_client():
    """Serve the real application with all trusted-model paths unavailable."""
    with (
        patch("app.predictor.load", side_effect=FileNotFoundError("synthetic missing bundle")),
        patch("app.predictor.loaded", False),
        patch("app.preprocess"),
        patch("app.distilbert_predictor.load", side_effect=FileNotFoundError("synthetic missing deep model")),
    ):
        with TestClient(app) as client:
            yield client


def test_homepage_is_served_without_model_readiness(unavailable_client):
    response = unavailable_client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "TruthScan" in response.text
    assert "/static/app.js" in response.text


def test_health_reports_unavailable_trusted_models(unavailable_client):
    response = unavailable_client.get("/health")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["models_loaded"] is False
    assert body["api_version"] == "2.0.0"
    assert isinstance(body["uptime_seconds"], (int, float))


def test_valid_looking_analysis_never_returns_prediction(unavailable_client):
    with patch("routers.api.predictor.predict") as predict:
        response = unavailable_client.post(
            "/analyze",
            json={
                "title": "Synthetic smoke-test title",
                "text": "This synthetic article is long enough for the request contract.",
            },
        )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Inference unavailable: trusted model artifacts are not ready."
    )
    assert "ensemble_label" not in response.json()
    assert "ensemble_is_fake" not in response.json()
    predict.assert_not_called()


def test_malformed_analysis_is_rejected_without_success(unavailable_client):
    with patch("routers.api.predictor.predict") as predict:
        response = unavailable_client.post(
            "/analyze",
            json={"title": "", "text": "too short"},
        )

    assert response.status_code == 422
    assert response.json()["detail"]
    assert predict.call_count == 0
