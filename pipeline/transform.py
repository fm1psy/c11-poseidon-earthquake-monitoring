from datetime import datetime
import logging

example = [{'type': 'Feature',
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
                           'alert': 'error',
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






PAGER_ALERT_LEVELS = ['green', 'yellow', 'orange', 'red']
READING_STATUS = ['automatic', 'reviewed', 'deleted']
NETWORKS = ['ak', 'at', 'ci', 'hv', 'ld', 'mb', 'nc', 'nm', 'nn', 'pr', 'pt', 'se', 'us', 'uu', 'uw']
MAGNITUDE_TYPES = ['md', 'ml', 'ms', 'mw', 'me', 'mi', 'mb', 'mlg']
EARTHQUAKE_TYPES = ['earthquake', 'quarry']
MAX_MAGNITUDE = 10.0
MIN_MAGNITUDE = -1.0
MAX_LON = 180.0
MIN_LON = -180.0
MAX_LAT = 90.0
MIN_LAT = -90.0
MAX_DEPTH = 1000
MIN_DEPTH = 0
MAX_CDI = 12.0
MIN_CDI = 1.0
MAX_MMI = 12.0
MIN_MMI = 1.0
MAX_SIG = 1000
MIN_SIG = 0
MAX_GAP = 360.0
MIN_GAP = 0.0

def convert_epoch_to_utc(time_in_ms: int) -> datetime:
    """
    Given epoch, it converts it to human-readable format
    """

    full_date = datetime.datetime.fromtimestamp(
        time_in_ms / 1000, tz=datetime.timezone.utc)
    
    return full_date.strftime("%H:%M")


def get_earthquake_property(data:dict, property_name: str) -> int | str | None:
    """
    Gets earthquake properties from the api data
    """
    try:
        if 'properties' not in data:
            logging.error('Missing earthquake properties')
            return None
        elif property_name not in data['properties']:
            logging.error('Property "%s" not in data', property_name)
            return None
        else:
            return data['properties'][property_name]
        
    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')
        return None

def get_earthquake_geometry(data: dict, geometry_param: str) -> int | None:
    """
    Gets earthquake properties from the api data
    """
    geometry_index = {'lon': 0, 'lat': 1, 'depth': 2}
    try:
        if 'geometry' not in data:
            logging.error('Missing earthquake geometry')
            return None
        if 'coordinates' not in data['geometry']:
            logging.error('Missing earthquake geometry coordinates')
            return None
        if geometry_param not in geometry_index:
            logging.error('Invalid geometry parameter: "%s"', geometry_param)
            return None
        if len(data['geometry']['coordinates']) != 3:
            logging.error('Earthquake geometry coordinates missing either lon/lat/depth')
            return None
        return data['geometry']['coordinates'][geometry_index[geometry_param]]
    
    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')
        return None


def get_earthquake_id(data):
    """
    Gets earthquake id from api data
    """
    try:
        if 'id' not in data:
            logging.error('Missing earthquake id')
            return None
        return data['id']
    except Exception as e:
        logging.error(f'An unexpected error occurred: {e}')
        return None

def get_earthquake_data(data):
    earthquake_id = get_earthquake_id(data)
    alert = get_earthquake_property(data, 'alert')  #validate_property
    status = get_earthquake_property(data, 'status')  # validate_property
    network = get_earthquake_property(data, 'net')  # validate_property
    magtype = get_earthquake_property(data, 'magType')  # validate_property
    earthquake_type = get_earthquake_property(data, 'type')  # validate_property
    magnitude = get_earthquake_property(data, 'mag') #validate_reading
    lon = get_earthquake_geometry(data, 'lon')  # validate_reading
    lat = get_earthquake_geometry(data, 'lat')  # validate_reading
    depth = get_earthquake_geometry(data, 'depth')  # validate_reading
    time = get_earthquake_property(data, 'time')  # TODO
    felt = get_earthquake_property(data, 'felt')  # TODO
    cdi = get_earthquake_property(data, 'cdi')  # validate_reading
    mmi = get_earthquake_property(data, 'mmi')  # validate_reading
    significance = get_earthquake_property(data, 'sig')  # validate_reading
    nst = get_earthquake_property(data, 'nst')  # TODO
    dmin = get_earthquake_property(data, 'dmin')  # TODO
    gap = get_earthquake_property(data, 'gap')  # validate_reading
    title = get_earthquake_property(data, 'title') #TODO

    return {
        'earthquake_id': earthquake_id,
        'alert': validate_property(alert, 'alert'),
        'status': status,
        'network': network,
        'magtype': magtype,
        'earthquake_type': earthquake_type,
        'magnitude': magnitude,
        'longitude': lon,
        'latitude': lat,
        'depth': depth,
        'time': time,
        'felt': felt,
        'cdi': cdi,
        'mmi': mmi,
        'significance': significance,
        'nst': nst,
        'dmin': dmin,
        'gap': gap,
        'title': title
    }

def validate_property(value, property):
    """
    This function can validate earthquake readings for: 
    alert, status, network, magtype and type.
    """
    valid_values = {
        'alert': PAGER_ALERT_LEVELS,
        'status': READING_STATUS,
        'network': NETWORKS,
        'magtype': MAGNITUDE_TYPES,
        'type': EARTHQUAKE_TYPES
    }

    if not isinstance(value, str):
        logging.error('Invalid data type: expected string')
        return None
    if value.lower() not in valid_values[property]:
        logging.error(f'{property.title()} not recognised. '
                    f'Value must be: {", ".join(valid_values[property])}')
        return None
    
    return value.lower()


def validate_reading(reading, reading_type):
    reading_types = {
        'mag': [MAX_MAGNITUDE, MIN_MAGNITUDE],
        'lon': [MAX_LON, MIN_LON],
        'lat': [MAX_LAT, MIN_LAT],
        'depth': [MAX_DEPTH, MIN_DEPTH],
        'cdi': [MAX_CDI, MIN_CDI],
        'mmi': [MAX_MMI, MIN_MMI],
        'sig': [MAX_SIG, MIN_SIG],
        'gap': [MAX_GAP, MIN_GAP]
    }

    max_value = reading_types[reading_type][0]
    min_value = reading_types[reading_type][1]

    if not isinstance(reading, float) or not isinstance(reading, int):
        logging.error('Invalid data type: expected a number')
        return None

    if not (min_value <= reading <= max_value):
        logging.error(f'Magnitude value {reading} out of range. '
                      f'Value must be between {min_value} and {max_value}.')
        return None

    return reading


def clean_data(data):
    ...

def transform_process():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    return [get_earthquake_data(data)for data in example]
       

if __name__ == "__main__":
    
    print(transform_process())


