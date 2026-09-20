import pytest
import pandas as pd
from fastapi.testclient import TestClient
from app import app


HELD_OUT_PATH = "tests/fixtures/nasa_test_sample.csv"

@pytest.fixture(scope="module")
def client():
    # Context manager triggers lifespan to actually load models natively
    with TestClient(app) as c:
        yield c

def test_nasa_held_out_articles(client):
    held_out = pd.read_csv(HELD_OUT_PATH).fillna("")
    samples = pd.concat(
        [
            held_out[held_out["class"] == 0].sample(n=2, random_state=1),
            held_out[held_out["class"] == 1].sample(n=2, random_state=1),
        ]
    ).sort_index()

    for row in samples.itertuples(index=False):
        response = client.post("/analyze", json={"title": row.title, "text": row.text})
        assert response.status_code == 200

        data = response.json()
        expected_is_fake = int(row[2]) == 0

        assert data["ensemble_is_fake"] is expected_is_fake
        assert data["ensemble_label"] == ("FAKE NEWS" if expected_is_fake else "REAL NEWS")
        assert data["overall_confidence"] > 50.0
        assert data["fake_votes"] + data["real_votes"] == data["total_models"]
        assert "processing_time_ms" in data
        assert data["processing_time_ms"] < 2000.0
        assert data["processed_length"] > 10
