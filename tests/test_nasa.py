import pytest
from fastapi.testclient import TestClient
from app import app

@pytest.fixture(scope="module")
def client():
    # Context manager triggers lifespan to actually load models natively
    with TestClient(app) as c:
        yield c

def test_nasa_real_news(client):
    payload = {
        "title": "NASA Launches New Mars Rover Mission Successfully",
        "text": (
            "NASA successfully launched its latest Mars rover mission on Monday "
            "from Cape Canaveral. The spacecraft is expected to reach Mars orbit "
            "in approximately seven months. Scientists from the Jet Propulsion "
            "Laboratory confirmed all systems are functioning normally after launch. "
            "The mission aims to search for signs of ancient microbial life and "
            "collect rock samples for future return to Earth."
        ),
    }

    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    # Assert correct verdict (Note: spaCy preprocessing shifts the model to predict REAL NEWS for this text)
    assert data["ensemble_label"] == "REAL NEWS"
    assert data["ensemble_is_fake"] is False
    
    # Assert weighted voting math
    assert data["overall_confidence"] > 50.0
    assert data["fake_votes"] + data["real_votes"] == data["total_models"]
    
    # Assert performance / response time logic
    assert "processing_time_ms" in data
    assert data["processing_time_ms"] < 2000.0  # spaCy pre-warming makes it fast
    assert data["processed_length"] > 10
