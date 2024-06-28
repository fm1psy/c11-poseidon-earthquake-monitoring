from unittest.mock import MagicMock
import pytest
from notifications import check_if_topic_exists, check_if_user_exists


def test_check_if_user_exists():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_user_info = {"email": 'test@test.com', "phone_number": "1234"}

    check_if_user_exists(mock_conn, mock_user_info)

    call_args = mock_cursor.execute.call_args[0]
    assert "select user_id from users" in call_args[0]
    assert "where email_address =" in call_args[0]
    assert "phone_number =" in call_args[0]


def test_check_if_topic_exists():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_user_info = {"selected_lat": '23',
                      "selected_lon": "134", "magnitude": '3'}

    check_if_topic_exists(mock_conn, mock_user_info)

    call_args = mock_cursor.execute.call_args[0]
    assert "select topic_id, topic_arn from topics" in call_args[0]
    assert "where min_magnitude=" in call_args[0]
    assert "and lon=" in call_args[0]
    assert "and lat=" in call_args[0]
