"""This file is responsible for downloading the latest earthquake data"""
import datetime
import requests

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
FEATURES = "features"
PROPERTIES = "properties"
TIME = "time"


def get_minute_from_epoch_time(time_in_ms: int) -> datetime:
    """Given epoch, it converts it to human-readable format"""
    if not isinstance(time_in_ms, int):
        raise TypeError("The input time_in_ms must be an integer.")

    if time_in_ms < 0:
        raise ValueError("The input time_in_ms cannot be negative.")

    return datetime.datetime.fromtimestamp(time_in_ms / 1000, tz=datetime.timezone.utc).minute


def get_all_earthquake_data(data_url: str) -> list[dict]:
    """Gets all earthquake data for the hour from USGS"""

    try:
        response = requests.get(data_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        if FEATURES not in data:
            raise KeyError(f"Expected key '{
                FEATURES}' not found in the response")
        return data[FEATURES]
    except requests.exceptions.Timeout as e:
        print(f"Timeout occurred in get_all_earthquake_data: {e}")
        return []
    except requests.exceptions.RequestException as e:
        print(f"RequestException occurred in get_all_earthquake_data: {e}")
        return []


def get_current_earthquake_data(all_earthquake_data: list[dict]) -> list[dict]:
    """Gets all the most recent earthquakes from data"""
    try:
        current_minute = datetime.datetime.now().minute
        latest_earthquakes = []

        for earthquake in all_earthquake_data:
            if PROPERTIES in earthquake and TIME in earthquake[PROPERTIES]:
                if get_minute_from_epoch_time(earthquake[PROPERTIES][TIME]) == current_minute:
                    latest_earthquakes.append(earthquake)
            else:
                raise KeyError("Key properties missing from data")
        return latest_earthquakes
    except Exception as e:
        print(f"Unexpected error occurred in get_current_earthquake_data: {e}")
        return []


def extract_process() -> list[dict]:
    """Runs the functions to extract all relevant data"""
    try:
        all_data = get_all_earthquake_data(URL)
        relevant_data = get_current_earthquake_data(all_data)
        return relevant_data
    except Exception as e:
        print("Error occurred in the extract process: " + e)
        return []
