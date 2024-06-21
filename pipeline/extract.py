"""This file is responsible for downloading the latest earthquake data"""
# pylint: disable=W0718

import datetime
import logging

import requests

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
FEATURES = "features"
PROPERTIES = "properties"
TIME = "time"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")


def get_time_from_epoch_time(time_in_ms: int) -> str:
    """Given epoch, it converts it to human-readable format"""
    if not isinstance(time_in_ms, int):
        raise TypeError("The input time_in_ms must be an integer.")

    if time_in_ms < 0:
        raise ValueError("The input time_in_ms cannot be negative.")

    full_date = datetime.datetime.fromtimestamp(
        time_in_ms / 1000, tz=datetime.timezone.utc)
    return full_date.strftime("%H:%M")


def get_all_earthquake_data(data_url: str) -> list[dict]:
    """Gets all earthquake data for the hour from USGS"""
    try:
        response = requests.get(data_url, timeout=30)
    except requests.exceptions.Timeout as e:
        logging.error(f"Timeout occurred in get_all_earthquake_data: {e}")
        return []
    except requests.exceptions.RequestException as e:
        logging.error(
            f"RequestException occurred in get_all_earthquake_data: {e}")
        return []

    response.raise_for_status()
    data = response.json()
    if FEATURES not in data:
        raise KeyError(f"Expected key '{FEATURES}' not found in the response")
    logging.info("Fetched all data")
    return data[FEATURES]


def get_current_earthquake_data(all_earthquake_data: list[dict]) -> list[dict]:
    """Gets all the most recent earthquakes from data"""
    try:
        time_to_compare_to = datetime.datetime.now(
            tz=datetime.timezone.utc) - datetime.timedelta(minutes=1)
        time_to_compare_to_formatted = time_to_compare_to.strftime("%H:%M")
        latest_earthquakes = []

        logging.info("Extracting recent earthquakes")
        for earthquake in all_earthquake_data:
            if PROPERTIES in earthquake and TIME in earthquake[PROPERTIES]:
                # if get_time_from_epoch_time(earthquake[PROPERTIES][TIME]) == time_to_compare_to_formatted or get_time_from_epoch_time(earthquake[PROPERTIES]["updated"]) == time_to_compare_to_formatted:
                latest_earthquakes.append(earthquake)
            else:
                logging.info("Skipping data, keys are missing")
                continue
        return latest_earthquakes
    except Exception as e:
        logging.error(
            f"Unexpected error occurred in get_current_earthquake_data: {e}")
        return latest_earthquakes


def extract_process() -> list[dict]:
    """Runs the functions to extract all relevant data"""
    try:
        all_data = get_all_earthquake_data(URL)
        relevant_data = get_current_earthquake_data(all_data)
        return relevant_data
    except Exception as e:
        logging.error(f"Error occurred in the extract process: {e}")
        return relevant_data


if __name__ == "__main__":
    print(extract_process())
