# pylint: skip-file

import logging
from datetime import datetime, timezone, timedelta
from extract import get_time_from_epoch_time, get_all_earthquake_data, get_current_earthquake_data
from unittest.mock import MagicMock, patch
import pytest


def test_get_time_from_epoch_time(get_epoch_time):
    minute_old_time = datetime.now(timezone.utc) - timedelta(minutes=1)
    assert get_time_from_epoch_time(
        get_epoch_time) == minute_old_time.strftime("%H:%M")


def test_get_invalid_minute_from_epoch_time():
    with pytest.raises(ValueError):
        get_time_from_epoch_time(-1)


def test_get_invalid_type_minute_from_epoch_time():
    with pytest.raises(TypeError):
        get_time_from_epoch_time("12345")


def test_get_all_earthquake_data(setup_mock_response, get_test_data_with_random_time):
    setup_mock_response(get_test_data_with_random_time)

    result = get_all_earthquake_data("test.com")
    assert result == get_test_data_with_random_time["features"]


def test_get_all_earthquake_without_feature_key(setup_mock_response,  get_test_data_without_features):
    setup_mock_response(get_test_data_without_features)

    with pytest.raises(KeyError):
        get_all_earthquake_data(get_test_data_without_features)


def test_get_current_earthquake_data(get_test_data_with_minute_old_time):
    assert len(get_current_earthquake_data(
        get_test_data_with_minute_old_time)) == 1


def test_get_current_earthquake_data_with_malformed_data(get_test_data_without_time, caplog):
    with caplog.at_level(logging.INFO):
        get_current_earthquake_data(get_test_data_without_time)
    assert any(
        "Skipping data, keys are missing" in message for message in caplog.text.splitlines())
