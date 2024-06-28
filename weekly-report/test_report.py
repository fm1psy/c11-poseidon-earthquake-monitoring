# pylint: skip-file
from report import previous_monday, get_file_keys_from_bucket, get_prefix, monday_week_date
import datetime
from unittest.mock import MagicMock


def test_get_prefix():
    input = datetime.date(2020, 5, 17)
    assert get_prefix(input) == "wc-11-05-2020/"


def test_monday_week_date():
    input = datetime.date(2020, 5, 17)
    assert monday_week_date(input) == "11-05-2020"


def test_previous_monday():
    input = datetime.date(2020, 5, 17)
    assert previous_monday(input) == datetime.date(2020, 5, 11)


def test_get_file_keys_from_bucket():
    mock_client = MagicMock()
    mock_client.list_objects.return_value = {
        "Contents": [
            {"Key": "file1.txt"},
            {"Key": "file2.txt"},
            {"Key": "file3.txt"}
        ]
    }

    expected_result = ["file1.txt", "file2.txt", "file3.txt"]

    assert get_file_keys_from_bucket(
        mock_client, "test-bucket") == expected_result
