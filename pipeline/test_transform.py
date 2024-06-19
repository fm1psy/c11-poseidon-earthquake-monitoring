from transform import *

extracted_data = [{'type': 'Feature',
                   'properties': {'mag': 0.67,
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
                                  'title': 'M 0.7 - 13 km WSW of Searles Valley, CA'},
                   'geometry': {'type': 'Point', 'coordinates': [-117.542, 35.7305, 1.88]},
                   'id': 'ci40801680'}]


def validate_time(time_in_ms: int) -> str:
    """
    Used to validate the time, given an epoch value
    """
    if time_in_ms is None:
        logging.error('No recorded value')
        return None

    current_time = datetime.now(timezone.utc)

    if not isinstance(time_in_ms, int):
        logging.error('Invalid data type: expected int')
        return current_time.strftime("%d/%m/%Y %H:%M:%S")

    recording_time = convert_epoch_to_utc(time_in_ms)

    if recording_time > current_time:
        logging.error('Future earthquake cannot be predicted')
        return current_time.strftime("%d/%m/%Y %H:%M:%S")

    return recording_time.strftime("%d/%m/%Y %H:%M:%S")

print(type(validate_time(3242425)))