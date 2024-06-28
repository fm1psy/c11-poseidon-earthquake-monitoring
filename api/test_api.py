# pylint: skip-file
import pytest
from api import STATUS_FILTER_KEY, NETWORK_FILTER_KEY, ALERT_FILTER_KEY, MAG_TYPE_FILTER_KEY, EVENT_FILTER_KEY, MIN_MAGNITUDE_FILTER_KEY, CONTINENT_FILTER_KEY, COUNTRY_FILTER_KEY, get_filter_queries, filter_by_continent, filter_by_country, filter_by_location, is_continent_valid, get_earthquake_data
from unittest.mock import patch


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


@patch("api.get_earthquake_data")
def test_endpoint_get_earthquakes_error_handling(mock_all_earthquakes, client):
    mock_all_earthquakes.side_effect = ValueError
    response = client.get("/earthquakes")
    assert response.status_code == 400
    assert "error" in response.json


@patch("api.get_connection")
@patch("api.get_filter_queries")
@patch("api.get_cursor")
@patch("api.filter_by_location")
def test_get_earthquake_data_function_calls(mock_location_filter, mock_cursor, mock_filter_queries, mock_connection):
    test_filter_dict = {
        STATUS_FILTER_KEY: "status",
        NETWORK_FILTER_KEY: "net",
        ALERT_FILTER_KEY: "alert",
        MAG_TYPE_FILTER_KEY: "magtype",
        EVENT_FILTER_KEY: "type",
        MIN_MAGNITUDE_FILTER_KEY: "min mag",
        CONTINENT_FILTER_KEY: "continent",
        COUNTRY_FILTER_KEY: "country"
    }
    get_earthquake_data(test_filter_dict)
    mock_location_filter.assert_called_once == True
    mock_cursor.assert_called_once == True
    mock_filter_queries.assert_called_once == True
    mock_connection.assert_called_once == True


def test_get_filter_queries():
    test_filter_dict = {
        STATUS_FILTER_KEY: "status",
        NETWORK_FILTER_KEY: "net",
        ALERT_FILTER_KEY: "alert",
        MAG_TYPE_FILTER_KEY: "magtype",
        EVENT_FILTER_KEY: "type",
        MIN_MAGNITUDE_FILTER_KEY: "min mag",
        CONTINENT_FILTER_KEY: "continent",
        COUNTRY_FILTER_KEY: "country"
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
        CONTINENT_FILTER_KEY: "continent",
        COUNTRY_FILTER_KEY: "country"
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


def test_filter_by_continent_invalid_continent(example_api_response):
    assert filter_by_continent(
        example_api_response, "Coney Island") == example_api_response


def test_filter_by_continent_error_handling(caplog):
    error_data = [{}, {}]
    filter_by_continent(error_data, "Africa")
    assert "Error appending data row (continent): " in caplog.text


def test_filter_by_country_error_handling(caplog):
    error_data = [{}, {}]
    filter_by_country(error_data, "Ecuador")
    assert "Error appending data row (country): " in caplog.text


def test_filter_by_country(example_api_response):
    assert filter_by_country(example_api_response,
                             "China") == []
    assert filter_by_country(example_api_response,
                             "United States") == example_api_response


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
