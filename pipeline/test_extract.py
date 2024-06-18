from datetime import datetime, timezone
from extract import get_minute_from_epoch_time


def test_get_minute_from_epoch_time():
    current_time = datetime(2024, 6, 18, 14, 8, tzinfo=timezone.utc)
    assert get_minute_from_epoch_time(
        int(current_time.timestamp() * 1000)) == current_time.minute
