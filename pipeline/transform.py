from datetime import datetime, timezone
import logging

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
    """
    Fetches each data point from the api, and returns it as a dictionary
    """
    earthquake_id = get_earthquake_id(data)  # validate_earthquake_naming
    alert = get_earthquake_property(data, 'alert')  #validate_property
    status = get_earthquake_property(data, 'status')  # validate_property
    network = get_earthquake_property(data, 'net')  # validate_property
    magtype = get_earthquake_property(data, 'magType')  # validate_property
    earthquake_type = get_earthquake_property(data, 'type')  # validate_property
    magnitude = get_earthquake_property(data, 'mag') #validate_reading
    lon = get_earthquake_geometry(data, 'lon')  # validate_reading
    lat = get_earthquake_geometry(data, 'lat')  # validate_reading
    depth = get_earthquake_geometry(data, 'depth')  # validate_reading
    time = get_earthquake_property(data, 'time')  # convert_epoch_to_utc
    felt = get_earthquake_property(data, 'felt')  # validate_inputs
    cdi = get_earthquake_property(data, 'cdi')  # validate_reading
    mmi = get_earthquake_property(data, 'mmi')  # validate_reading
    significance = get_earthquake_property(data, 'sig')  # validate_reading
    nst = get_earthquake_property(data, 'nst')  # validate_inputs
    dmin = get_earthquake_property(data, 'dmin')  # validate_dmin
    gap = get_earthquake_property(data, 'gap')  # validate_reading
    title = get_earthquake_property(data, 'title') #validate_earthquake_naming

    return {
        'earthquake_id': earthquake_id,
        'alert': alert,
        'status': status,
        'network': network,
        'magtype': magtype,
        'earthquake_type': earthquake_type,
        'magnitude': magnitude,
        'lon': lon,
        'lat': lat,
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


def validate_earthquake_naming(name):
    """
    Used to validate earthquake_id and title
    """
    if name == None:
        logging.error('No recorded value')
        return None

    if not isinstance(name, str):
        logging.error('Invalid data type: expected string')
        return None

    return name


def convert_epoch_to_utc(time_in_ms: int):
    """
    Given epoch, it converts it into: DD/MM/YYYY HH:MM:SS
    """
    return datetime.fromtimestamp(time_in_ms / 1000, tz=timezone.utc)


def validate_time(time_in_ms: int) -> datetime:
    """
    Used to validate the time, given an epoch value
    """
    if time_in_ms == None:
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


def validate_inputs(input):
    """
    Used to validate data where data has been inputted manually,
    checks number of people who felt the earthquake and number of
    stations which recorded the earthquake
    """
    if input == None:
        logging.error('No recorded value')
        return None
    
    if not isinstance(input, int):
        logging.error('Invalid data type: expected int')
        return None

    if input < 0:
        logging.error('{input} cannot be below 0')
        return None

    return input


def validate_dmin(dmin: float) -> None | float:
    """
    Used to validate 
    """
    if dmin == None:
        logging.error('No recorded value')
        return None
    
    if not isinstance(dmin, float):
        logging.error('Invalid data type: expected int')
        return None

    if dmin < 0:
        logging.error('dmin cannot be below 0')
        return None

    return dmin


def validate_property(value, property):
    """
    This function can validate earthquake readings for: 
    alert, status, network, magtype and type.
    """

    if value == None:
        logging.error('No recorded value')
        return None
    
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
    if reading == None:
        logging.error('No recorded value')
        return None
    
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

    if not isinstance(reading, (float, int)):
        logging.error('Invalid data type: expected a number')
        return None

    if not (min_value <= reading <= max_value):
        logging.error(f'Magnitude value {reading} out of range. '
                      f'Value must be between {min_value} and {max_value}.')
        return None

    return reading


def clean_data(data):
    return {
        'earthquake_id': validate_earthquake_naming(data['earthquake_id']),
        'alert': validate_property(data['alert'], 'alert'),
        'status': validate_property(data['status'], 'status'),
        'network': validate_property(data['network'], 'network'),
        'magtype': validate_property(data['magtype'], 'magtype'),
        'earthquake_type': validate_property(data['earthquake_type'], 'type'),
        'magnitude': validate_reading(data['magnitude'], 'mag'),
        'lon': validate_reading(data['lon'], 'lon'),
        'lat': validate_reading(data['lat'], 'lat'),
        'depth': validate_reading(data['depth'], 'depth'),
        'time': validate_time(data['time']),
        'felt': validate_inputs(data['felt']),
        'cdi': validate_reading(data['cdi'], 'cdi'),
        'mmi': validate_reading(data['mmi'], 'mmi'),
        'significance': validate_reading(data['significance'], 'sig'),
        'nst': validate_inputs(data['nst']),
        'dmin': validate_dmin(data['dmin']),
        'gap': validate_reading(data['gap'], 'gap'),
        'title': validate_earthquake_naming(data['title'])
    }


def transform_process(extracted_data):

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    latest_data = [get_earthquake_data(data)for data in extracted_data]
    print(latest_data)
    print('\n')
    return [clean_data(data) for data in latest_data]

if __name__ == "__main__":
    
    print(transform_process(extracted_data))

