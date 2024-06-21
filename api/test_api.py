# pylint: skip-file
from dotenv import load_dotenv
import pytest
from api import app
from unittest.mock import patch

load_dotenv()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_endpoint_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json


@patch("api.get_all_earthquakes")
def test_endpoint_get_earthquakes(mock_all_earthquakes, client):
    mock_all_earthquakes.return_value = [{"test": "output"}]
    response = client.get("/earthquakes")
    assert response.status_code == 200
    assert isinstance(response.json, list)
