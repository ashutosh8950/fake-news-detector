import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from app import app

@pytest.fixture(autouse=True)
def mock_predictor_env():
    with patch("app.predictor.load"), \
         patch("app.predictor.loaded", True), \
         patch("app.predictor.meta", {"mock": {"name": "Mock Model", "accuracy": 100.0, "f1": 100.0}}), \
         patch("app.predictor.get_model_info", return_value={"mock": {"name": "Mock Model", "accuracy": 100.0, "f1": 100.0}}), \
         patch("app.preprocess"):
        yield

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["models_loaded"] is True

def test_models_info(client):
    response = client.get("/models/info")
    assert response.status_code == 200
    data = response.json()
    assert "mock" in data

@patch("app.predictor.predict")
def test_analyze_real_news(mock_predict, client):
    mock_predict.return_value = {
        "ensemble_is_fake": False,
        "ensemble_label": "REAL NEWS",
        "overall_confidence": 98.0,
        "fake_votes": 1,
        "real_votes": 4,
        "total_models": 5,
        "models": {},
        "processed_length": 50,
        "processing_time_ms": 1.0
    }
    payload = {
        "title": "NASA Launches New Mars Rover Mission Successfully",
        "text": "NASA successfully launched its latest Mars rover mission on Monday from Cape Canaveral."
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ensemble_label"] == "REAL NEWS"
    assert data["ensemble_is_fake"] is False

@patch("app.predictor.predict")
def test_analyze_fake_news(mock_predict, client):
    mock_predict.return_value = {
        "ensemble_is_fake": True,
        "ensemble_label": "FAKE NEWS",
        "overall_confidence": 99.0,
        "fake_votes": 5,
        "real_votes": 0,
        "total_models": 5,
        "models": {},
        "processed_length": 45,
        "processing_time_ms": 1.0
    }
    payload = {
        "title": "SHOCKING: Government Putting Microchips in COVID Vaccines",
        "text": "A whistleblower from inside the government has revealed that all COVID-19 vaccines contain microscopic chips."
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["ensemble_label"] == "FAKE NEWS"
    assert data["ensemble_is_fake"] is True

def test_frontend_serving(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    html = response.text
    assert "TruthScan" in html
