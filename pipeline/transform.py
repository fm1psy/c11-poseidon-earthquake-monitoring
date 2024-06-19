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
    magnitude = get_earthquake_property(data, 'mag')
    lon = get_earthquake_geometry(data, 'lon')
    lat = get_earthquake_geometry(data, 'lat')
    depth = get_earthquake_geometry(data, 'depth')
    time = get_earthquake_property(data, 'time')
    felt = get_earthquake_property(data, 'felt')
    cdi = get_earthquake_property(data, 'cdi') #intensity
    mmi = get_earthquake_property(data, 'mmi') #intensity
    significance = get_earthquake_property(data, 'sig')
    nst = get_earthquake_property(data,'nst') #number of stations
    dmin = get_earthquake_property(data, 'dmin') #station distance from epicentre, smaller is better
    gap = get_earthquake_property(data, 'gap') #gap between 2 stations
    title = get_earthquake_property(data, 'title') 

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

def validate_magnitude(magnitude):
    if 0.0 <= magnitude <= 10.0:
        return True
    else:
        logging.error(f'Magnitude value {magnitude} out of range. '
                      f'Value must be between {0.0} and {10.0}.')
        return False

def clean_data(data):
    ...

def transform_process():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    return [get_earthquake_data(data)for data in example]
       

if __name__ == "__main__":
    
    print(transform_process())


