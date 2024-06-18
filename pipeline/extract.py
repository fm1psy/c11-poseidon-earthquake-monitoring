"""This file is responsible for downloading the latest earthquake data"""
import datetime
import requests

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
FEATURES = "features"
PROPERTIES = "properties"
TIME = "time"


def get_minute_from_epoch_time(time_in_ms: int) -> datetime:
    """Given epoch, it converts it to human-readable format"""
    return datetime.datetime.fromtimestamp(time_in_ms/1000, tz=datetime.timezone.utc).minute


def get_all_earthquake_data(data_url: str) -> list[dict]:
    """Gets all earthquake data for the hour from USGS"""
    response = requests.get(data_url, timeout=30)
    data = response.json()
    return data[FEATURES]


def get_current_earthquake_data(all_earthquake_data: list[dict]) -> list[dict]:
    """Gets all the most recent earthquakes from data"""
    current_minute = datetime.datetime.now().minute
    latest_earthquakes = []

    for earthquake in all_earthquake_data:
        print(get_minute_from_epoch_time(earthquake[PROPERTIES][TIME]))
        if get_minute_from_epoch_time(earthquake[PROPERTIES][TIME]) == current_minute:
            latest_earthquakes.append(earthquake)

    return latest_earthquakes


def extract_process() -> list[dict]:
    """Runs the functions to extract all the latest earthquakes"""
    all_data = get_all_earthquake_data(URL)
    relevant_data = get_current_earthquake_data(all_data[FEATURES])
    return relevant_data
