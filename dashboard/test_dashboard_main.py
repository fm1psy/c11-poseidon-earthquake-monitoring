from main import get_usa_only_earthquakes, get_magnitude_map_data_last_30_days, get_magnitude_map_data_last_7_days, get_most_recent_earthquake_above_mag_6, get_avg_magnitude_last_30_days, get_avg_magnitude_last_7_days
from unittest.mock import MagicMock
import pytest


def test_fetch_magnitude_map_data_last_7_days():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    get_magnitude_map_data_last_7_days(mock_conn)

    call_args = mock_cursor.execute.call_args[0]
    assert "SELECT lon,lat,magnitude,depth FROM earthquakes" in call_args[0]
    assert "WHERE time >= %s" in call_args[0]


def test_fetch_magnitude_map_data_last_30_days():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    get_magnitude_map_data_last_30_days(mock_conn)

    call_args = mock_cursor.execute.call_args[0]
    assert "SELECT lon,lat,magnitude,depth FROM earthquakes" in call_args[0]
    assert "WHERE time >= %s" in call_args[0]


def test_fetch_usa_only_earthquakes():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    get_usa_only_earthquakes(mock_conn)

    call_args = mock_cursor.execute.call_args[0]
    assert "SELECT lon,lat,magnitude, depth FROM earthquakes" in call_args[0]


def test_get_most_recent_earthquake_above_6():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    get_most_recent_earthquake_above_mag_6(mock_conn)

    call_args = mock_cursor.execute.call_args[0]
    assert "select title, time, magnitude from earthquakes" in call_args[0]
    assert "where magnitude >= 6" in call_args[0]
    assert "order by time DESC limit 1" in call_args[0]


def test_get_avg_magnitude_last_7_days():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    get_avg_magnitude_last_7_days(mock_conn)

    call_args = mock_cursor.execute.call_args[0]
    assert "SELECT AVG(magnitude)" in call_args[0]


def test_get_avg_magnitude_last_30_days():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    get_avg_magnitude_last_30_days(mock_conn)

    call_args = mock_cursor.execute.call_args[0]
    assert "SELECT AVG(magnitude)" in call_args[0]
