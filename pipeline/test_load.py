import pytest
import logging
from psycopg2 import OperationalError
from unittest.mock import MagicMock, patch
from load import execute_query, execute_insert, fetch_all, get_or_add_id, add_earthquake_data_to_rds


def test_execute_query(mock_cursor):
    mock_cursor.execute.return_value = MagicMock()
    test_return_value = {"alert_id": 1, "alert_value": "green"}
    mock_cursor.fetchall.return_value = [test_return_value]
    query = "SELECT * FROM alerts"

    result = execute_query(mock_cursor, query)

    mock_cursor.fetchall.assert_called_once()
    assert result == [test_return_value]


def test_execute_query_generic_error(mock_cursor, caplog):
    mock_cursor.execute = MagicMock(side_effect=Exception("Example error"))
    query = "SELECT * FROM alerts"

    with caplog.at_level(logging.INFO):
        execute_query(mock_cursor, query)
    assert any(
        "An unexpected error occurred while executing query" in message for message in caplog.text.splitlines())


def test_execute_query_operational_error(mock_cursor, caplog):
    mock_cursor.execute = MagicMock(
        side_effect=OperationalError("Example operational error"))
    query = "SELECT * FROM alerts"

    with caplog.at_level(logging.INFO):
        execute_query(mock_cursor, query)
    assert any(
        "OperationalError occurred while executing query" in message for message in caplog.text.splitlines())


def test_execute_insert(mock_cursor, mock_connection):
    column_to_get = "alert_id"
    test_return_value = {column_to_get: 1}
    test_query = "INSERT INTO alerts VALUE 'blue'"
    mock_cursor.execute.return_value = MagicMock()
    mock_cursor.fetchone.return_value = test_return_value
    mock_connection.commit.return_value = MagicMock()

    result = execute_insert(mock_connection, mock_cursor,
                            test_query, ("blue",), column_to_get)

    mock_connection.commit.assert_called_once()
    assert result == 1


def test_execute_insert_operational_error(mock_cursor, mock_connection, caplog):
    mock_cursor.execute = MagicMock(
        side_effect=OperationalError("Example operational error"))

    with caplog.at_level(logging.ERROR):
        execute_insert(mock_connection, mock_cursor,
                       "test_query", ("blue",), "test")
    assert any(
        "Database error" in message for message in caplog.text.splitlines())


def test_execute_insert_generic_error(mock_cursor, mock_connection, caplog):
    mock_cursor.execute = MagicMock(
        side_effect=Exception("Example exception"))

    with caplog.at_level(logging.ERROR):
        execute_insert(mock_connection, mock_cursor,
                       "test_query", ("blue",), "test")
    assert any(
        "Unexpected error occurred while adding to the database" in message for message in caplog.text.splitlines())


def test_fetch_all(mock_cursor):
    with patch("load.execute_query") as mock:
        mock.return_value = [{"alert_id": 1, "alert_value": "green"}, {
            "alert_id": 2, "alert_value": "orange"}, {"alert_id": 3, "alert_value": "red"}]

        assert fetch_all(mock_cursor, "alerts", "alert_value", "alert_id") == {
            "green": 1, "orange": 2, "red": 3}


def test_fetch_all_with_empty_list(mock_cursor):
    with patch("load.execute_query") as mock:
        mock.return_value = []

        assert fetch_all(mock_cursor, "alerts",
                         "alert_value", "alert_id") == {}


def test_get_or_add_id_with_value_in_dict():
    assert get_or_add_id("test", {"test": 1}, "test") == 1


def test_get_or_add_id_with_new_value():
    new_value = "blue"
    all_items = {"green": 1}
    add_to_db_function = MagicMock(return_value=2)

    result = get_or_add_id(new_value, all_items, add_to_db_function)

    assert result == 2
    add_to_db_function.assert_called_once_with(new_value)
    assert all_items[new_value] == 2


def test_add_earthquake_data_to_rds(mock_connection, mock_cursor, example_transformed_data, caplog, example_id_tables):
    all_alerts, all_statuses, all_networks, all_magtypes, all_types = example_id_tables

    with patch("load.get_network_id", return_value=1) as mock_get_network_id, \
            patch("load.get_magtype_id", return_value=1) as mock_get_magtype_id, \
            patch("load.get_type_id", return_value=1) as mock_get_type_id:

        with caplog.at_level(logging.INFO):
            add_earthquake_data_to_rds(mock_connection, mock_cursor, example_transformed_data,
                                       all_alerts, all_statuses, all_networks, all_magtypes, all_types)
        mock_cursor.execute.assert_called_once()
        mock_connection.commit.assert_called_once()
        mock_get_network_id.assert_called_once_with(
            mock_connection, mock_cursor, "ak", all_networks)
        mock_get_magtype_id.assert_called_once_with(
            mock_connection, mock_cursor, "ml", all_magtypes)
        mock_get_type_id.assert_called_once_with(
            mock_connection, mock_cursor, "earthquake", all_types)
        assert any(
            "Successfully added earthquake" in message for message in caplog.text.splitlines())


def test_add_earthquake_data_with_db_error(mock_connection, mock_cursor, example_transformed_data, caplog, example_id_tables):
    all_alerts, all_statuses, all_networks, all_magtypes, all_types = example_id_tables
    mock_cursor.execute = MagicMock(
        side_effect=OperationalError("Example operational error"))

    with patch("load.get_network_id", return_value=1), patch("load.get_magtype_id", return_value=1), patch("load.get_type_id", return_value=1):
        with caplog.at_level(logging.ERROR):
            add_earthquake_data_to_rds(mock_connection, mock_cursor, example_transformed_data,
                                       all_alerts, all_statuses, all_networks, all_magtypes, all_types)
        assert any(
            "Database error" in message for message in caplog.text.splitlines())


def test_add_earthquake_data_with_generic_error(mock_connection, mock_cursor, example_transformed_data, caplog, example_id_tables):
    all_alerts, all_statuses, all_networks, all_magtypes, all_types = example_id_tables
    mock_cursor.execute = MagicMock(
        side_effect=Exception("Generic error"))

    with patch("load.get_network_id", return_value=1), patch("load.get_magtype_id", return_value=1), patch("load.get_type_id", return_value=1):
        with caplog.at_level(logging.ERROR):
            add_earthquake_data_to_rds(mock_connection, mock_cursor, example_transformed_data,
                                       all_alerts, all_statuses, all_networks, all_magtypes, all_types)
        assert any(
            "Unexpected error while adding earthquake data" in message for message in caplog.text.splitlines())
