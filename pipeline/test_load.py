import pytest
import logging
from psycopg2 import OperationalError
from unittest.mock import MagicMock
from load import execute_query, execute_insert


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
