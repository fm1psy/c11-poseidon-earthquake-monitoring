# pylint: disable=E1101, W0718, W1203, R0914

"""This file is responsible for cleaning and transforming the latest earthquake data"""

from datetime import datetime, timezone
import logging

PAGER_ALERT_LEVELS = ['green', 'yellow', 'orange', 'red']
READING_STATUS = ['automatic', 'reviewed', 'deleted']
NETWORK_NAME_LENGTH = 2
MAX_MAGNITUDE = 10.0
MIN_MAGNITUDE = -1.0
MAX_LON = 180.0
MIN_LON = -180.0
MAX_LAT = 90.0
MIN_LAT = -90.0
MAX_DEPTH = 1000
MIN_DEPTH = -100
MAX_CDI = 12.0
MIN_CDI = 0.0
MAX_MMI = 12.0
MIN_MMI = 0.0
MAX_SIG = 1000
MIN_SIG = 0
MAX_GAP = 360.0
MIN_GAP = 0.0
REQUIRED_FIELDS = ['lat', 'lon', 'magnitude', 'magtype']


def get_earthquake_property(data: dict, property_name: str) -> int | str | None:
    """
    Gets earthquake properties from the api data
    """
    try:
        if 'properties' not in data:
            logging.error('Missing earthquake properties')
            return None
        if property_name not in data['properties']:
            logging.error(f'Property "{property_name}" not in data')
            return None
        return data['properties'][property_name]

    except Exception as e:
        logging.error(f'An unexpected error occurred: {e} in getting "{property_name}"')
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
            logging.error(f'Invalid geometry parameter: {geometry_param}')
            return None
        if len(data['geometry']['coordinates']) != 3:
            logging.error(
                'Earthquake geometry coordinates missing either lon/lat/depth')
            return None
        return data['geometry']['coordinates'][geometry_index[geometry_param]]

    except Exception as e:
        logging.error(f'An unexpected error occurred: {e} in getting "{geometry_param}"')
        return None


def get_earthquake_id(data: dict) -> str | None:
    """
    Gets earthquake id from api data
    """
    try:
        if 'id' not in data:
            logging.error('Missing earthquake id')
            return None
        return data['id']
    except Exception as e:
        logging.error(f'An unexpected error occurred: {e} in getting "earthquake id"')
        return None


def get_earthquake_data(data: dict) -> dict:
    """
    Fetches each data point from the api, and returns it as a dictionary
    """
    earthquake_id = get_earthquake_id(data)  # validate_earthquake_naming
    alert = get_earthquake_property(data, 'alert')  # validate_property
    status = get_earthquake_property(data, 'status')  # validate_property
    network = get_earthquake_property(data, 'net')  # validate_network
    magtype = get_earthquake_property(data, 'magType')  # validate_types
    earthquake_type = get_earthquake_property(data, 'type')  # validate_types
    magnitude = get_earthquake_property(data, 'mag')  # validate_reading
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
    title = get_earthquake_property(
        data, 'title')  # validate_earthquake_naming

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


def validate_earthquake_naming(name: str, identifier) -> None | str:
    """
    Used to validate earthquake_id and title
    """
    if name is None or name == '':
        logging.error(f'No recorded value for "{identifier}"')
        return None

    if not isinstance(name, str):
        logging.error(f'Invalid data type: expected string in "{identifier}"')
        return None

    return name


def convert_epoch_to_utc(time_in_ms: int) -> datetime:
    """
    Given epoch, it converts it into: DD/MM/YYYY HH:MM:SS
    """
    return datetime.fromtimestamp(time_in_ms / 1000, tz=timezone.utc)


def validate_time(time_in_ms: int) -> str:
    """
    Used to validate the time, given an epoch value
    """
    if time_in_ms is None:
        logging.error('No recorded value for "earthquake time"')
        return None

    current_time = datetime.now(timezone.utc)

    if not isinstance(time_in_ms, int):
        logging.error('Invalid data type: expected int for time_in_ms')
        return current_time.strftime("%Y/%m/%d %H:%M:%S")

    recording_time = convert_epoch_to_utc(time_in_ms)

    if recording_time > current_time:
        logging.error('Future earthquake cannot be predicted')
        return current_time.strftime("%Y/%m/%d %H:%M:%S")

    return recording_time.strftime("%Y/%m/%d %H:%M:%S")


def validate_inputs(inputted_data: int, input_type: str) -> None | int:
    """
    Used to validate data where data has been inputted manually,
    checks number of people who felt the earthquake and number of
    stations which recorded the earthquake
    """
    if inputted_data is None:
        logging.error(f'No recorded value for "{input_type}"')
        return None

    if not isinstance(inputted_data, int) or isinstance(inputted_data, bool):
        logging.error(
            f'Invalid data type: expected int in inputs for "{input_type}"')
        return None

    if inputted_data < 0:
        logging.error(f'inputted_data for "{input_type}" cannot be below 0')
        return None

    return inputted_data


def validate_dmin(dmin: float | int) -> None | float | int:
    """
    Used to validate dmin which measures the closest horizontal distance
      from a seismic station, to where an earthquake happens
    """
    if dmin is None:
        logging.error('No recorded value for "dmin"')
        return None

    if not isinstance(dmin, (float, int)) or isinstance(dmin, bool):
        logging.error('Invalid data type: expected int in "dmin"')
        return None

    if dmin < 0:
        logging.error('"dmin" cannot be below 0')
        return None

    return dmin


def validate_types(eq_type: str, eq_type_name: str) -> str | None:
    """
    This function validates readings for :magtype and type.
    """
    if not isinstance(eq_type, str):
        logging.error(f'Invalid data type: expected a string for "{eq_type_name}"')
        return None

    return eq_type


def validate_network(network: str) -> str | None:
    """
    This function makes sure a valid network is entered
    """
    if not isinstance(network, str):
        logging.error('Invalid data type for "network": expected a string')
        return None

    if len(network) != NETWORK_NAME_LENGTH:
        logging.error(f'Invalid length for "network": expected {NETWORK_NAME_LENGTH}')
        return None

    return network


def validate_property(value: str, earthquake_property: str) -> None | str:
    """
    This function can validate earthquake readings for: 
    alert and status
    """
    if value is None or value == '':
        logging.error(f'No recorded value for "{earthquake_property}"')
        return None

    valid_values = {
        'alert': PAGER_ALERT_LEVELS,
        'status': READING_STATUS,
    }

    if not isinstance(value, str):
        logging.error(
            f'Invalid data type: expected string for "{earthquake_property}"')
        return None
    if value.lower() not in valid_values[earthquake_property]:
        logging.error(f'"{earthquake_property}" not recognised. '
                      f'Value must be: {", ".join(valid_values[earthquake_property])}')
        return None

    return value.lower()


def validate_reading(reading: float | int, reading_type: str) -> None | float | int:
    """
    This function can validate earthquake readings for:
    magnitude, longitude, latitude, depth, cdi, mmi, sig and gap
    """
    if reading is None:
        logging.error(f'No recorded value for "{reading_type}"')
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

    if not isinstance(reading, (float, int)) or isinstance(reading, bool):
        logging.error(f'Invalid data type: expected a number for "{reading_type}"')
        return None

    if not min_value <= reading <= max_value:
        logging.error(f'"{reading_type}" value {reading} out of range. '
                      f'Value must be between {min_value} and {max_value}.')
        return None

    return reading


def clean_data(data: dict) -> dict:
    """
    Function takes in the sorted values from `get_earthquake_data` and
    runs appropriate data validation checks to ensure that no erroneous
    data is recorded
    """
    return {
        'earthquake_id': validate_earthquake_naming(data['earthquake_id'], 'earthquake_id'),
        'alert': validate_property(data['alert'], 'alert'),
        'status': validate_property(data['status'], 'status'),
        'network': validate_network(data['network']),
        'magtype': validate_types(data['magtype'], 'magtype'),
        'earthquake_type': validate_types(data['earthquake_type'], 'earthquake_type'),
        'magnitude': validate_reading(data['magnitude'], 'mag'),
        'lon': validate_reading(data['lon'], 'lon'),
        'lat': validate_reading(data['lat'], 'lat'),
        'depth': validate_reading(data['depth'], 'depth'),
        'time': validate_time(data['time']),
        'felt': validate_inputs(data['felt'], 'felt'),
        'cdi': validate_reading(data['cdi'], 'cdi'),
        'mmi': validate_reading(data['mmi'], 'mmi'),
        'significance': validate_reading(data['significance'], 'sig'),
        'nst': validate_inputs(data['nst'], 'nst'),
        'dmin': validate_dmin(data['dmin']),
        'gap': validate_reading(data['gap'], 'gap'),
        'title': validate_earthquake_naming(data['title'], 'title')
    }


def is_valid_earthquake_data(data: dict) -> bool:
    """
    Checks if the earthquake data dictionary is valid.
    True if data is valid (contains 'lat', 'lon', 'magnitude', 'magtype'), False otherwise.
    """
    return all(field in data and data[field] is not None for field in REQUIRED_FIELDS)


def transform_process(extracted_data: list[dict]) -> list[dict]:
    """
    Runs the functions to transform and clean all extracted earthquake data.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    latest_data = [get_earthquake_data(data) for data in extracted_data]
    cleaned_data = [clean_data(data) for data in latest_data]
    valid_data = [data for data in cleaned_data if is_valid_earthquake_data(data)]

    return valid_data
