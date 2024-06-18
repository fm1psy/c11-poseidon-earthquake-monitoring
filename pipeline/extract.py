"""This file is responsible for downloading the latest earthquake data"""
from datetime import datetime
import requests

URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson"
FEATURES = "features"


def convert_time_to_current_time(time_in_ms: int) -> datetime:
    return datetime.timestamp(time_in_ms/1000)


response = requests.get(URL)
data = response.json()[FEATURES]
print(data)
