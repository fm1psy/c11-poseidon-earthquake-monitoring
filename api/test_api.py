# pylint: skip-file
from dotenv import load_dotenv
import pytest
from api import app, STATUS_FILTER_KEY, NETWORK_FILTER_KEY, ALERT_FILTER_KEY, MAG_TYPE_FILTER_KEY, EVENT_FILTER_KEY, MIN_MAGNITUDE_FILTER_KEY, CONTINENT_FILTER_KEY, COUNTRY_FILTER_KEY, get_filter_queries, filter_by_continent, filter_by_country, filter_by_location, is_continent_valid

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


@patch("api.get_earthquake_data")
def test_endpoint_get_earthquakes(mock_all_earthquakes, client):
    mock_all_earthquakes.return_value = [{"test": "output"}]
    response = client.get("/earthquakes")
    assert response.status_code == 200
    assert isinstance(response.json, list)


def test_get_filter_queries():
    test_filter_dict = {
        STATUS_FILTER_KEY: "status",
        NETWORK_FILTER_KEY: "net",
        ALERT_FILTER_KEY: "alert",
        MAG_TYPE_FILTER_KEY: "magtype",
        EVENT_FILTER_KEY: "type",
        MIN_MAGNITUDE_FILTER_KEY: "min mag",
        CONTINENT_FILTER_KEY: "continent"
    }

    assert get_filter_queries(test_filter_dict) == [
        "WHERE s.status = 'status'",
        "n.network_name = 'net'",
        "a.alert_value = 'alert'",
        "mt.magtype_value = 'magtype'",
        "t.type_value = 'type'",
        "e.magnitude >= 'min mag'"
    ]


def test_get_filter_queries_alert_is_first_filter():
    test_filter_dict = {
        STATUS_FILTER_KEY: None,
        NETWORK_FILTER_KEY: None,
        ALERT_FILTER_KEY: "alert",
        MAG_TYPE_FILTER_KEY: "magtype",
        EVENT_FILTER_KEY: "type",
        MIN_MAGNITUDE_FILTER_KEY: "min mag",
        CONTINENT_FILTER_KEY: "continent"
    }

    assert get_filter_queries(test_filter_dict) == [
        "WHERE a.alert_value = 'alert'",
        "mt.magtype_value = 'magtype'",
        "t.type_value = 'type'",
        "e.magnitude >= 'min mag'"
    ]


def test_filter_by_continent(example_api_response):
    assert filter_by_continent(example_api_response, "Africa") == []
    assert filter_by_continent(
        example_api_response, "North America") == example_api_response


def test_is_continent_valid():
    assert is_continent_valid("Asia") == True


def test_is_continent_invalid():
    assert is_continent_valid("Three") == False


@patch("api.filter_by_country")
@patch("api.filter_by_continent")
@pytest.mark.parametrize("inputs, expect", [(("china", "africa"), (True, False)),
                                            ((None, "africa"), (False, True)),
                                            (("china", None), (True, False)),
                                            ((None, None), (False, False))])
def test_filter_by_location(mock_continent_filter, mock_country_filter, inputs, expect):
    filter_by_location([{}, {}], inputs[0], inputs[1])
    mock_continent_filter.assert_called_once, mock_country_filter.assert_called_once == expect
