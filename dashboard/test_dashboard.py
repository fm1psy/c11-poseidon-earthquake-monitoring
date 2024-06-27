from main import get_usa_only_earthquakes, get_magnitude_map_data_last_30_days, get_magnitude_map_data_last_7_days
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
