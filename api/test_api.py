# pylint: skip-file
from dotenv import load_dotenv
import pytest
from api import app, status_FILTER_KEY, network_FILTER_KEY, alert_FILTER_KEY, mag_type_FILTER_KEY, event_FILTER_KEY, min_magnitude_FILTER_KEY, continent_FILTER_KEY, get_filter_queries

from unittest.mock import patch

load_dotenv()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture()
def example_api_response():
    return [
        {
            "alert": None,
            "cause_of_event": "earthquake",
            "cdi": None,
            "depth": 1.96,
            "dmin": 0.006074,
            "earthquake_id": "nc75025077",
            "felt": None,
            "gap": 165.0,
            "lat": "38.833332",
            "lon": "-122.878830",
            "magnitude": 0.78,
            "magtype": "md",
            "mmi": None,
            "network_name": "nc",
            "nst": 16,
            "significance": 9,
            "status": "automatic",
            "time": "Fri, 21 Jun 2024 20:18:40 GMT",
            "title": "M 0.8 - 12 km NW of The Geysers, CA"
        },
        {
            "alert": None,
            "cause_of_event": "earthquake",
            "cdi": None,
            "depth": 10.88,
            "dmin": 0.05398,
            "earthquake_id": "ci40806056",
            "felt": None,
            "gap": 63.0,
            "lat": "33.494499",
            "lon": "-116.480331",
            "magnitude": 1.04,
            "magtype": "ml",
            "mmi": None,
            "network_name": "ci",
            "nst": 26,
            "significance": 17,
            "status": "reviewed",
            "time": "Fri, 21 Jun 2024 20:16:06 GMT",
            "title": "M 1.0 - 19 km ESE of Anza, CA"
        },
        {
            "alert": None,
            "cause_of_event": "earthquake",
            "cdi": None,
            "depth": 2.02,
            "dmin": 0.008128,
            "earthquake_id": "nc75025072",
            "felt": None,
            "gap": 174.0,
            "lat": "38.821999",
            "lon": "-122.845337",
            "magnitude": 0.24,
            "magtype": "md",
            "mmi": None,
            "network_name": "nc",
            "nst": 8,
            "significance": 1,
            "status": "deleted",
            "time": "Fri, 21 Jun 2024 20:10:08 GMT",
            "title": "M 0.2 - 9 km NW of The Geysers, CA"
        }]


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


def test_get_filter_queries():
    test_filter_dict = {
        status_FILTER_KEY: "status",
        network_FILTER_KEY: "net",
        alert_FILTER_KEY: "alert",
        mag_type_FILTER_KEY: "magtype",
        event_FILTER_KEY: "type",
        min_magnitude_FILTER_KEY: "min mag",
        continent_FILTER_KEY: "continent"
    }

    assert get_filter_queries(test_filter_dict) == [
        "WHERE s.status = 'status'",
        "n.network_name = 'net'",
        "a.alert_value = 'alert'",
        "mt.magtype_value = 'magtype'",
        "t.type_value = 'type'",
        "e.magnitude >= 'min mag'",
        "NOT YET IMPLEMENTED"
    ]


def test_get_filter_queries_alert_is_first_filter():
    test_filter_dict = {
        status_FILTER_KEY: None,
        network_FILTER_KEY: None,
        alert_FILTER_KEY: "alert",
        mag_type_FILTER_KEY: "magtype",
        event_FILTER_KEY: "type",
        min_magnitude_FILTER_KEY: "min mag",
        continent_FILTER_KEY: "continent"
    }

    assert get_filter_queries(test_filter_dict) == [
        "WHERE a.alert_value = 'alert'",
        "mt.magtype_value = 'magtype'",
        "t.type_value = 'type'",
        "e.magnitude >= 'min mag'",
        "NOT YET IMPLEMENTED"
    ]
