from datetime import datetime, timezone
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock:
        yield mock


@pytest.fixture
def get_current_epoch_time():
    current_time = datetime.now(timezone.utc)
    return int(current_time.timestamp() * 1000)


@pytest.fixture
def setup_mock_response(mock_requests_get):
    def _setup_mock_response(mock_data):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_requests_get.return_value = mock_response
    return _setup_mock_response


@pytest.fixture
def get_test_data_with_random_time():
    return {
        "type": "FeatureCollection",
        "metadata": {
            "generated": 1718710860000,
            "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
            "title": "USGS All Earthquakes, Past Hour",
            "status": 200,
            "api": "1.10.3",
            "count": 4
        },
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "mag": 3.2,
                    "place": "88 km NW of Yakutat, Alaska",
                    "time": 1718710078388,
                    "updated": 1718710240631,
                    "tz": None,
                    "url": "https://earthquake.usgs.gov/earthquakes/eventpage/ak0247tc2ogk",
                    "detail": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/ak0247tc2ogk.geojson",
                    "felt": None,
                    "cdi": None,
                    "mmi": None,
                    "alert": None,
                    "status": "automatic",
                    "tsunami": 0,
                    "sig": 158,
                    "net": "ak",
                    "code": "0247tc2ogk",
                    "ids": ",ak0247tc2ogk,",
                    "sources": ",ak,",
                    "types": ",origin,phase-data,",
                    "nst": None,
                    "dmin": None,
                    "rms": 1.07,
                    "gap": None,
                    "magType": "ml",
                    "type": "earthquake",
                    "title": "M 3.2 - 88 km NW of Yakutat, Alaska"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [-140.7726, 60.1438, 0]
                },
                "id": "ak0247tc2ogk"
            },
            {
                "type": "Feature",
                "properties": {
                    "mag": 0.9,
                    "place": "6 km NNW of Houston, Alaska",
                    "time": 1718708469755,
                    "updated": 1718709252757,
                    "tz": None,
                    "url": "https://earthquake.usgs.gov/earthquakes/eventpage/ak0247tbx02t",
                    "detail": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/ak0247tbx02t.geojson",
                    "felt": None,
                    "cdi": None,
                    "mmi": None,
                    "alert": None,
                    "status": "automatic",
                    "tsunami": 0,
                    "sig": 12,
                    "net": "ak",
                    "code": "0247tbx02t",
                    "ids": ",ak0247tbx02t,",
                    "sources": ",ak,",
                    "types": ",origin,phase-data,",
                    "nst": None,
                    "dmin": None,
                    "rms": 0.56,
                    "gap": None,
                    "magType": "ml",
                    "type": "earthquake",
                    "title": "M 0.9 - 6 km NNW of Houston, Alaska"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [-149.8864, 61.6806, 29]
                },
                "id": "ak0247tbx02t"
            },
        ],
        "bbox": [-155.27699279785, 19.39049911499, 0, -117.0975, 61.6806, 29]
    }


@pytest.fixture
def get_test_data_with_current_time(get_current_epoch_time):
    return [
        {
            "type": "Feature",
            "properties": {
                "mag": 3.2,
                "place": "88 km NW of Yakutat, Alaska",
                "time": get_current_epoch_time,
                "updated": 1718710240631,
                "tz": None,
                "url": "https://earthquake.usgs.gov/earthquakes/eventpage/ak0247tc2ogk",
                "detail": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/ak0247tc2ogk.geojson",
                "felt": None,
                "cdi": None,
                "mmi": None,
                "alert": None,
                "status": "automatic",
                "tsunami": 0,
                "sig": 158,
                "net": "ak",
                "code": "0247tc2ogk",
                "ids": ",ak0247tc2ogk,",
                "sources": ",ak,",
                "types": ",origin,phase-data,",
                "nst": None,
                "dmin": None,
                "rms": 1.07,
                "gap": None,
                "magType": "ml",
                "type": "earthquake",
                "title": "M 3.2 - 88 km NW of Yakutat, Alaska"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-140.7726, 60.1438, 0]
            },
            "id": "ak0247tc2ogk"
        },
        {
            "type": "Feature",
            "properties": {
                "mag": 0.9,
                "place": "6 km NNW of Houston, Alaska",
                "time": 1718708469755,
                "updated": 1718709252757,
                "tz": None,
                "url": "https://earthquake.usgs.gov/earthquakes/eventpage/ak0247tbx02t",
                "detail": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/ak0247tbx02t.geojson",
                "felt": None,
                "cdi": None,
                "mmi": None,
                "alert": None,
                "status": "automatic",
                "tsunami": 0,
                "sig": 12,
                "net": "ak",
                "code": "0247tbx02t",
                "ids": ",ak0247tbx02t,",
                "sources": ",ak,",
                "types": ",origin,phase-data,",
                "nst": None,
                "dmin": None,
                "rms": 0.56,
                "gap": None,
                "magType": "ml",
                "type": "earthquake",
                "title": "M 0.9 - 6 km NNW of Houston, Alaska"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-149.8864, 61.6806, 29]
            },
            "id": "ak0247tbx02t"
        },
    ]


@pytest.fixture
def get_test_data_without_features():
    return {
        "type": "FeatureCollection",
        "metadata": {
            "generated": 1718710860000,
            "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_hour.geojson",
            "title": "USGS All Earthquakes, Past Hour",
            "status": 200,
            "api": "1.10.3",
            "count": 4
        }
    }


@pytest.fixture
def get_test_data_without_time():
    return [
        {
            "type": "Feature",
            "properties": {
                "mag": 3.2,
                "place": "88 km NW of Yakutat, Alaska",
                "updated": 1718710240631,
                "tz": None,
                "url": "https://earthquake.usgs.gov/earthquakes/eventpage/ak0247tc2ogk",
                "detail": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/ak0247tc2ogk.geojson",
                "felt": None,
                "cdi": None,
                "mmi": None,
                "alert": None,
                "status": "automatic",
                "tsunami": 0,
                "sig": 158,
                "net": "ak",
                "code": "0247tc2ogk",
                "ids": ",ak0247tc2ogk,",
                "sources": ",ak,",
                "types": ",origin,phase-data,",
                "nst": None,
                "dmin": None,
                "rms": 1.07,
                "gap": None,
                "magType": "ml",
                "type": "earthquake",
                "title": "M 3.2 - 88 km NW of Yakutat, Alaska"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [-140.7726, 60.1438, 0]
            },
            "id": "ak0247tc2ogk"
        }
    ]
