# pylint: skip-file

from datetime import datetime, timezone, timedelta
import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock:
        yield mock


@pytest.fixture
def get_epoch_time():
    current_time = datetime.now(timezone.utc) - timedelta(minutes=1)
    return int(current_time.timestamp() * 1000)


@pytest.fixture
def get_current_utc_time():
    current_time = datetime.now(timezone.utc)
    return current_time.strftime("%Y/%m/%d %H:%M:%S")


@pytest.fixture
def setup_mock_response(mock_requests_get):
    def _setup_mock_response(mock_data):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_requests_get.return_value = mock_response
    return _setup_mock_response


@pytest.fixture
def mock_connection():
    with patch("psycopg2.connect") as mock:
        yield mock


@pytest.fixture
def mock_cursor(mock_connection):
    mocked_cursor = MagicMock()
    mock_connection.cursor.return_value = mocked_cursor
    return mocked_cursor


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
def get_test_data_with_minute_old_time(get_epoch_time):
    return [
        {
            "type": "Feature",
            "properties": {
                "mag": 3.2,
                "place": "88 km NW of Yakutat, Alaska",
                "time": get_epoch_time,
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


@pytest.fixture
def example_reading():
    return {'type': 'Feature',
            'properties': {'mag': 0.67,
                           'place': '13 km WSW of Searles Valley, CA',
                           'time': 1718718656830,
                           'updated': 1718720255694,
                           'tz': None,
                           'url': 'https://earthquake.usgs.gov/earthquakes/eventpage/ci40801680',
                           'detail': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/ci40801680.geojson',
                           'felt': None,
                           'cdi': 5.6,
                           'mmi': 6.0,
                           'alert': 'red',
                           'status': 'reviewed',
                           'tsunami': 0,
                           'sig': 7,
                           'net': 'ci',
                           'code': '40801680',
                           'ids': ',ci40801680,',
                           'sources': ',ci,',
                                      'types': ',nearby-cities,origin,phase-data,scitech-link,',
                                      'nst': 17,
                                      'dmin': 0.1163,
                                      'rms': 0.13,
                                      'gap': 146,
                                      'magType': 'ml',
                                      'type': 'earthquake',
                                      'title': 'M 0.7 - 13 km WSW of Searles Valley, CA'},
            'geometry': {'type': 'Point', 'coordinates': [-117.542, 35.7305, 1.88]},
            'id': 'ci40801680'}


@pytest.fixture
def example_reading_missing_values():
    return {
        'type': 'Feature',
        'properties': {
            'mag': 0.67,
            'place': '13 km WSW of Searles Valley, CA',
            'time': 1718718656830,
            'updated': 1718720255694,
            'tz': None,
            'url': 'https://earthquake.usgs.gov/earthquakes/eventpage/ci40801680',
            'detail': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/ci40801680.geojson',
            'felt': None,
            'cdi': None,
            'mmi': None,
            'alert': None,
            'status': 'reviewed',
            'tsunami': 0,
            'sig': 7,
            'net': 'ci',
            'code': '40801680',
            'ids': ',ci40801680,',
            'sources': ',ci,',
            'types': ',nearby-cities,origin,phase-data,scitech-link,',
            'nst': 17,
            'dmin': 0.1163,
            'rms': 0.13,
            'gap': 146,
            'magType': 'ml',
            'type': 'earthquake',
            'title': 'M 0.7 - 13 km WSW of Searles Valley, CA'
        },
        'geometry': {
            'type': 'Point',
            'coordinates': [-117.542, 35.7305, 1.88]
        },
        'id': 'ci40801680'
    }


@pytest.fixture
def empty_reading():
    return {
    }


@pytest.fixture
def example_reading_missing_coordinates():
    return {
        'type': 'Feature',
        'properties': {
            'mag': 0.67,
            'place': '13 km WSW of Searles Valley, CA',
            'time': 1718718656830,
            'updated': 1718720255694,
            'tz': None,
            'url': 'https://earthquake.usgs.gov/earthquakes/eventpage/ci40801680',
            'detail': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/ci40801680.geojson',
            'felt': None,
            'cdi': None,
            'mmi': None,
            'alert': None,
            'status': 'reviewed',
            'tsunami': 0,
            'sig': 7,
            'net': 'ci',
            'code': '40801680',
            'ids': ',ci40801680,',
            'sources': ',ci,',
            'types': ',nearby-cities,origin,phase-data,scitech-link,',
            'nst': 17,
            'dmin': 0.1163,
            'rms': 0.13,
            'gap': 146,
            'magType': 'ml',
            'type': 'earthquake',
            'title': 'M 0.7 - 13 km WSW of Searles Valley, CA'
        },
        'geometry': {
            'type': 'Point'
        },
        'id': 'ci40801680'
    }


@pytest.fixture
def example_reading_missing_depth():
    return {
        'type': 'Feature',
        'properties': {
            'mag': 0.67,
            'place': '13 km WSW of Searles Valley, CA',
            'time': 1718718656830,
            'updated': 1718720255694,
            'tz': None,
            'url': 'https://earthquake.usgs.gov/earthquakes/eventpage/ci40801680',
            'detail': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/ci40801680.geojson',
            'felt': None,
            'cdi': None,
            'mmi': None,
            'alert': None,
            'status': 'reviewed',
            'tsunami': 0,
            'sig': 7,
            'net': 'ci',
            'code': '40801680',
            'ids': ',ci40801680,',
            'sources': ',ci,',
            'types': ',nearby-cities,origin,phase-data,scitech-link,',
            'nst': 17,
            'dmin': 0.1163,
            'rms': 0.13,
            'gap': 146,
            'magType': 'ml',
            'type': 'earthquake',
            'title': 'M 0.7 - 13 km WSW of Searles Valley, CA'
        },
        'geometry': {
            'type': 'Point',
            'coordinates': [-117.542, 35.7305]
        },
        'id': 'ci40801680'
    }


@pytest.fixture
def example_erroneous_reading():
    return {
        'type': 'Feature',
        'properties': {
            'mag': 0.67,
            'place': '13 km WSW of Searles Valley, CA',
            'time': 33109056003843,
            'updated': 1718720255694,
            'tz': None,
            'url': 'https://earthquake.usgs.gov/earthquakes/eventpage/ci40801680',
            'detail': 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/ci40801680.geojson',
            'felt': None,
            'cdi': None,
            'mmi': '10.1',
            'alert': 'hot pink',
            'status': 'reviewed',
            'tsunami': 0,
            'sig': 7,
            'net': 'ci',
            'code': '40801680',
            'ids': ',ci40801680,',
            'sources': ',ci,',
            'types': ',nearby-cities,origin,phase-data,scitech-link,',
            'nst': 9.9,
            'dmin': 0.1163,
            'rms': 0.13,
            'gap': 146,
            'magType': 'ml',
            'type': 'earthquake',
            'title': 'M 0.7 - 13 km WSW of Searles Valley, CA'
        },
        'geometry': {
            'type': 'Point',
            'coordinates': [-17.542, 35.7305, -1000]
        },
        'id': 'c3820fd332'
    }


@pytest.fixture
def example_transformed_data(get_epoch_time):
    return [{
        "earthquake_id": "ak0247tc2ogk",
        "alert": "green",
        "status": "automatic",
        "network": "ak",
        "magtype": "ml",
        "earthquake_type": "earthquake",
        "magnitude": 3.2,
        "lon": -140.7726,
        "lat": 60.1438,
        "depth": 0,
        "time": get_epoch_time,
        "felt": None,
        "cdi": None,
        "mmi": None,
        "significance": 158,
        "nst": None,
        "dmin": None,
        "gap": None,
        "title": "M 3.2 - 88 km NW of Yakutat, Alaska"
    }]


@pytest.fixture
def example_id_tables():
    return {"green": 1}, {"automatic": 1, "reviewed": 2}, {"ak": 1}, {"ml": 1}, {"earthquake": 1}

@pytest.fixture
def liverpool_earthquake():
    return [{
        "earthquake_id": "ak0247tc2ogk",
        "alert": "green",
        "status": "automatic",
        "network": "ak",
        "magtype": "ml",
        "earthquake_type": "earthquake",
        "magnitude": 6.0,
        "lon": -2.964996,
        "lat": 53.407624,
        "depth": 0,
        "time": '2024-06-24 12: 22: 22',
        "felt": None,
        "cdi": None,
        "mmi": None,
        "significance": 158,
        "nst": None,
        "dmin": None,
        "gap": None,
        "title": "M 3.2 - 88 km NW of Yakutat, Alaska"
    }]




@pytest.fixture
def example_topic():
    return {'topic_id': 12, 'topic_arn': 'arn:aws:sns:eu-west-2:129033205317:c11-poseidon-test_email',
            'min_magnitude': 4.5, 'lon': -2.964996, 'lat': 53.407624}


@pytest.fixture
def example_topics():
    return [
        {'topic_id': 8, 'topic_arn': 'arn:aws:sns:us-east-1:123456789012:ExampleTopic',
            'min_magnitude': 4.5, 'lon': -73.935242, 'lat': 40.730610},
        {'topic_id': 9, 'topic_arn': 'arn:aws:sns:us-west-2:123456789012:AnotherTopic',
            'min_magnitude': 3.8, 'lon': -122.419418, 'lat': 37.774929},
        {'topic_id': 10, 'topic_arn': 'arn:aws:sns:eu-west-1:123456789012:ThirdTopic',
            'min_magnitude': 5.2, 'lon': 0.127800, 'lat': 51.507400},
        {'topic_id': 11, 'topic_arn': 'arn:aws:sns:eu-west-2:129033205317:c11-poseidon-test',
            'min_magnitude': 3.0, 'lon': 140.053711, 'lat': 38.203655},
        {'topic_id': 12, 'topic_arn': 'arn:aws:sns:eu-west-2:129033205317:c11-poseidon-test_email',
            'min_magnitude': 4.5, 'lon': -2.964996, 'lat': 53.407624}
    ]


@pytest.fixture
def example_user():
    return {
        'user_id': 22,
        'email_address': 'trainee.joe.lam@sigmalabs.co.uk',
        'phone_number': '447482569206',
        'topic_arn': 'arn:aws:sns:eu-west-2:129033205317:c11-poseidon-test_email',
        'min_magnitude': 4.5
    }

    # cursor = get_cursor(conn)
    # with cursor as cur:
    #     for topic in related_topics:
    #         query = """
    #         SELECT uta.user_id, u.email_address, u.phone_number, t.topic_arn, t.min_magnitude
    #         FROM user_topic_assignments AS uta
    #         JOIN users AS u ON u.user_id = uta.user_id
    #         JOIN topics AS t ON uta.topic_id = t.topic_id
    #         WHERE uta.topic_id = %s;
    #         """
    #         cur.execute(query, (topic['topic_id'],))
    #         rows = cur.fetchall()
    #         return [get_user_information(row) for row in rows]

# z
# def get_user_information(user):
#     return {
#         'user_id': user['user_id'],
#         'email_address': user['email_address'],
#         'phone_number': user['phone_number'],
#         'topic_arn': user['topic_arn'],
#         'min_magnitude': user['min_magnitude']
#     }
