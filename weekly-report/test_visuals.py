# pylint: skip-file
from visuals import get_magnitude_map_data, get_top_significant_earthquakes, get_top_magnitude_earthquake
from visuals import get_total_number_earthquakes, get_usa_only_earthquakes
from unittest.mock import MagicMock
import pytest


def test_fetch_magnitude_map_data():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    get_magnitude_map_data(mock_conn)

    call_args = mock_cursor.execute.call_args[0]
    assert "SELECT lon,lat,magnitude,depth FROM earthquakes" in call_args[0]
    assert "WHERE time >= %s" in call_args[0]


def test_fetch_top_significant_earthquakes():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    get_top_significant_earthquakes(mock_conn)

    call_args = mock_cursor.execute.call_args[0]
    assert "SELECT title, significance FROM earthquakes" in call_args[0]
    assert "WHERE time >= %s" in call_args[0]


def test_fetch_top_magnitude_earthquake():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    get_top_magnitude_earthquake(mock_conn)

    call_args = mock_cursor.execute.call_args[0]
    assert "SELECT title, magnitude FROM earthquakes" in call_args[0]
    assert "WHERE time >= %s" in call_args[0]


def test_fetch_total_number_earthquakes():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    get_total_number_earthquakes(mock_conn)

    call_args = mock_cursor.execute.call_args[0]
    assert "SELECT COUNT(*) FROM earthquakes" in call_args[0]
    assert "WHERE time >= %s" in call_args[0]


def test_fetch_usa_only_earthquakes():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    get_usa_only_earthquakes(mock_conn)

    call_args = mock_cursor.execute.call_args[0]
    assert "SELECT lon,lat,magnitude, depth FROM earthquakes" in call_args[0]
    assert "WHERE time >= %s" in call_args[0]
