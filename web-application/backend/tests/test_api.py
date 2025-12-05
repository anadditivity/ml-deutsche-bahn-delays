import json
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from app import app


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


def test_stations_no_filter(client):
    resp = client.get("/stations")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]


def test_stations_with_filter(client):
    resp = client.get("/stations?name=a")
    assert resp.status_code == 200
    data = resp.get_json()
    for s in data:
        assert "a" in s["name"].lower()


def test_lines_no_filter(client):
    resp = client.get("/lines")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_predict_missing_fields(client):
    resp = client.post(
        "/predict",
        data=json.dumps({}),
        content_type="application/json",
    )
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
