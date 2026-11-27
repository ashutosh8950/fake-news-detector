"""Synthetic end-to-end smoke tests for the unavailable-model application state."""

from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app import app


@pytest.fixture
def unavailable_client():
    with patch("app.predictor.load", side_effect=FileNotFoundError("synthetic missing bundle")), \
         patch("app.predictor.loaded", False):
        with TestClient(app) as client:
            yield client


def test_unavailable_application_serves_ui_and_truthful_readiness(unavailable_client):
    health = unavailable_client.get("/health")
    assert health.status_code == 503
    assert health.json() == {
        "status": "not_ready",
        "models_loaded": False,
        "uptime_seconds": health.json()["uptime_seconds"],
        "api_version": "2.0.0",
    }

    page = unavailable_client.get("/")
    assert page.status_code == 200
    assert "TruthScan" in page.text
    assert "/static/app.js" in page.text

    javascript = unavailable_client.get("/static/app.js")
    assert javascript.status_code == 200
    assert "API available · models unavailable" in javascript.text
    assert "setStatus('offline', 'API Offline')" in javascript.text
    assert "Model metrics unavailable — trusted model artifacts are not ready." in javascript.text
    assert "the API may be offline or still starting" in javascript.text
    assert "the API may still be starting. Retrying with the next health check." not in javascript.text

    contract = unavailable_client.get("/static/response_contract.js")
    assert contract.status_code == 200
    assert "TruthScanResponseContract" in contract.text


def test_unavailable_inference_never_returns_prediction(unavailable_client):
    response = unavailable_client.post(
        "/analyze",
        json={
            "title": "Synthetic title",
            "text": "This synthetic article is long enough for the request contract.",
        },
    )

    assert response.status_code == 503
    assert "ensemble_label" not in response.json()
    assert response.json()["detail"] == (
        "Inference unavailable: trusted model artifacts are not ready."
    )


def test_invalid_request_is_rejected_before_inference(unavailable_client):
    response = unavailable_client.post(
        "/analyze",
        json={"title": "", "text": "too short"},
    )

    assert response.status_code == 422
    assert response.json()["detail"]


def test_frontend_handles_malformed_or_offline_responses_without_backend_changes(unavailable_client):
    javascript = unavailable_client.get("/static/app.js").text

    # These are source-level integration assertions because no browser driver
    # is installed in the verified environment. They ensure the real served
    # frontend has controlled branches for fetch failures and bad JSON.
    assert "catch {" in javascript
    assert "showError(err.message || 'Could not reach the API?" not in javascript
    assert "showError(err.message || 'Could not reach the API. Is the server running?')" in javascript
    assert "res.json().catch(() => ({}))" in javascript
    assert "data.status === 'not_ready'" in javascript
    assert "The API returned an invalid response. Please try again." in javascript
    assert "els.results.hidden = true" in javascript


def test_track_b_is_not_imported_by_track_a_application(unavailable_client):
    application_source = unavailable_client.get("/static/app.js").text
    assert "synthetic_claim_api" not in application_source
    assert "/claim" not in application_source
    route_paths = set(app.openapi()["paths"])
    assert "/analyze" in route_paths
    assert "/claim" not in route_paths
