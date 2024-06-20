from transform import *
import pytest
import logging
import datetime

@pytest.mark.parametrize("property_name, expected_value", [
    ('mag', 0.67),
    ('time', 1718718656830),
    ('felt', None),
    ('cdi', 5.6),
    ('mmi', 6.0),
    ('alert','red'),
    ('status','reviewed'),
    ('sig', 7),
    ('net', 'ci'),
    ('nst', 17),
    ('dmin', 0.1163),
    ('rms', 0.13),
    ('gap', 146),
    ('magType', 'ml'),
    ('type', 'earthquake'),
    ('title', 'M 0.7 - 13 km WSW of Searles Valley, CA'),
])
def test_get_earthquake_property_valid(example_reading, property_name, expected_value):
    assert get_earthquake_property(example_reading, property_name) == expected_value



@pytest.mark.parametrize("property_name, expected_value", [
    ('mag', 0.67),
    ('non_existent_property', None),
])
def test_get_earthquake_property_invalid_key(example_reading_missing_values, property_name, expected_value, caplog):
    with caplog.at_level(logging.ERROR):
        assert get_earthquake_property(example_reading_missing_values, property_name) == expected_value
        if expected_value is None:
            assert 'Property "non_existent_property" not in data' in caplog.messages
        else:
            assert not caplog.messages


def test_get_earthquake_property_missing_data(empty_reading, caplog):  
    with caplog.at_level(logging.ERROR):
        assert get_earthquake_property(
            empty_reading, 'mag') == None
        assert 'Missing earthquake properties' in caplog.messages


def test_get_earthquake_property_random_error():
    with pytest.raises(Exception):
        get_earthquake_property()


@pytest.mark.parametrize("geometry_param, expected_value", [
    ('lon', -117.542),
    ('lat', 35.7305),
    ('depth', 1.88),
])
def test_get_earthquake_geometry_valid(example_reading, geometry_param, expected_value):
    assert get_earthquake_geometry(
        example_reading, geometry_param) == expected_value


def test_get_earthquake_geometry_missing_geometry(empty_reading, caplog):
    with caplog.at_level(logging.ERROR):
        assert get_earthquake_geometry(
            empty_reading, 'lon') == None
        assert 'Missing earthquake geometry' in caplog.messages


def test_get_earthquake_geometry_missing_coordinates(example_reading_missing_coordinates, caplog):
    with caplog.at_level(logging.ERROR):
        assert get_earthquake_geometry(
            example_reading_missing_coordinates, 'long') == None
        assert 'Missing earthquake geometry coordinates' in caplog.messages


@pytest.mark.parametrize("geometry_param, expected_value", [
    ('lon', -117.542),
    ('non_existent_property', None),
])
def test_get_get_earthquake_geometry_invalid_parameter(example_reading_missing_values, geometry_param, expected_value, caplog):
    with caplog.at_level(logging.ERROR):
        assert get_earthquake_geometry(
            example_reading_missing_values, geometry_param) == expected_value
        if expected_value is None:
            assert 'Invalid geometry parameter: non_existent_property' in caplog.messages
        else:
            assert not caplog.messages


def test_get_earthquake_geometry_missing_depth(example_reading_missing_depth, caplog):
    with caplog.at_level(logging.ERROR):
        assert get_earthquake_geometry(
            example_reading_missing_depth, 'lon') == None
        assert 'Earthquake geometry coordinates missing either lon/lat/depth' in caplog.messages


def test_get_earthquake_geometry_random_error():
    with pytest.raises(Exception):
        get_earthquake_geometry()


def test_get_earthquake_id_valid(example_reading):
    assert get_earthquake_id(example_reading) == 'ci40801680'


def test_get_earthquake_id_missing_id(empty_reading, caplog):
    with caplog.at_level(logging.ERROR):
        assert get_earthquake_id(empty_reading) == None
        assert 'Missing earthquake id' in caplog.messages


def test_get_earthquake_id_random_error():
    with pytest.raises(Exception):
        get_earthquake_id()


def test_get_earthquake_data(example_reading):
    assert get_earthquake_data(example_reading) == {
        'earthquake_id': 'ci40801680',
        'alert': 'red',
        'status': 'reviewed',
        'network': 'ci',
        'magtype': 'ml',
        'earthquake_type': 'earthquake',
        'magnitude': 0.67,
        'lon': -117.542,
        'lat': 35.7305,
        'depth': 1.88,
        'time': 1718718656830,
        'felt': None,
        'cdi': 5.6,
        'mmi': 6.0,
        'significance': 7,
        'nst': 17,
        'dmin': 0.1163,
        'gap': 146,
        'title': 'M 0.7 - 13 km WSW of Searles Valley, CA'
    }


@pytest.mark.parametrize("name, identifier, expected_value", [
    ('M 0.7 - 13 km WSW of Searles Valley, CA', 'title', 'M 0.7 - 13 km WSW of Searles Valley, CA'),
    ('ci40801680', 'earthquake_id', 'ci40801680'),
    (12345, 'title', None),
    (['ci40801680'], 'earthquake_id', None),
    ({'id': 'ci40801680'}, 'earthquake_id', None),
    ('ak0247tbx02t', 'earthquake_id', 'ak0247tbx02t'),
    ('M 0.9 - 6 km NNW of Houston, Alaska', 'title',
     'M 0.9 - 6 km NNW of Houston, Alaska'),
    (('M 0.9 - 6 km NNW of Houston, Alaska', 'ak0247tbx02t'), 'title', None),
    ('M 3.2 - 5 km ESE of Ojai, CA', 'title', 'M 3.2 - 5 km ESE of Ojai, CA'),
    ('us7000d1jv', 'earthquake_id','us7000d1jv'),
    ('M 4.5 - 10 km NE of Pahala, Hawaii', 'title',
     'M 4.5 - 10 km NE of Pahala, Hawaii'),
    ('M 2.1 - Off the coast of Oregon', 'title', 'M 2.1 - Off the coast of Oregon'),
    ('ci20173338', 'earthquake_id','ci20173338'),
    ('us1000h8sf', 'earthquake_id','us1000h8sf'),
    (True, 'earthquake_id', None),
    (False, 'earthquake_id', None),
    (1.23, 'earthquake_id', None),
])
def test_validate_earthquake_naming(name, identifier, expected_value, caplog):
    with caplog.at_level(logging.ERROR):
        assert validate_earthquake_naming(name, identifier) == expected_value
        if expected_value is None:
            assert f'Invalid data type: expected string in "{identifier}"' in caplog.messages
        else:
            assert not caplog.messages


@pytest.mark.parametrize("name, identifier,expected_value", [
    ('', 'title', None),
    (None, 'earthquake_id', None)
])
def test_validate_earthquake_naming_no_value(name, identifier, expected_value, caplog):
    with caplog.at_level(logging.ERROR):
        assert validate_earthquake_naming(name, identifier) == expected_value
        assert f'No recorded value for "{identifier}"' in caplog.messages


@ pytest.mark.parametrize("time_in_ms, expected_value", [
    (0, datetime.datetime(1970, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)),
    (1609459200000, datetime.datetime(2021, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)),
    (1718708469755, datetime.datetime(2024, 6, 18, 11, 1, 9, 755000, tzinfo=datetime.timezone.utc)),
    (1893456000000, datetime.datetime(2030, 1, 1, 0, 0, tzinfo=datetime.timezone.utc)),
])
def test_convert_epoch_to_utc(time_in_ms, expected_value):
    assert convert_epoch_to_utc(time_in_ms) == expected_value


@pytest.mark.parametrize("time_in_ms, expected_value", [
    (0, '1970/01/01 00:00:00'),
    (1609459200000, '2021/01/01 00:00:00'),
    (1718708469755, '2024/06/18 11:01:09'),
    (33109056003843, 'future_date'),
    ('1609459200000', 'string'),
    ([1609459200000], 'list'),
    ({'date': 1609459200000}, 'dict'),
    (None, None),
])
def test_validate_time(time_in_ms, expected_value, get_current_utc_time, caplog):
    if expected_value in ['future_date', 'string', 'list', 'dict']:
        expected_value = get_current_utc_time
    assert validate_time(time_in_ms) == expected_value
    if expected_value is None:
        assert 'No recorded value for "earthquake time"' in caplog.messages


def test_validate_time_invalid_data_type(get_current_utc_time, caplog):
    assert validate_time('error') == get_current_utc_time
    assert 'Invalid data type: expected int for time_in_ms' in caplog.messages


def test_validate_time_future_time(get_current_utc_time, caplog):
    assert validate_time(33109056003843) == get_current_utc_time
    assert 'Future earthquake cannot be predicted' in caplog.messages


@pytest.mark.parametrize("inputted_data, input_type ,expected_value", [
    (2345, 'felt', 2345),
    (12, 'nst', 12),
    (2,'felt',2),
    (12.5,'felt', None),
    (10.2, 'nst', None),
    (0, 'nst', 0),
    (-1, 'felt', None),
    ('12', 'nst', None),
    ([12, 24], 'felt', None),
    ({'input': 34}, 'nst', None),
    (None, 'nst', None),
    (0, 'felt', 0),
    (0.1, 'felt', None),
    (1, 'felt', 1),
    (-1, 'nst', None),
    (1234567890, 'felt', 1234567890), 
    (1e6, 'nst', None), 
    (True, 'nst', None), 
    (False, 'felt', None), 
    ([], 'nst', None),
    ({}, 'felt', None),
    (set(), 'nst', None), 
])
def test_validate_inputs(inputted_data, input_type, expected_value):
    assert validate_inputs(inputted_data, input_type) == expected_value


def test_validate_inputs_no_reading(caplog):
    assert validate_inputs(None, 'felt') == None
    assert 'No recorded value for "felt"' in caplog.messages


def test_validate_inputs_invalid_data_type(caplog):
    assert validate_inputs(12.0, 'felt') == None
    assert 'Invalid data type: expected int in inputs for "felt"' in caplog.messages


def test_validate_inputs_negative(caplog):
    assert validate_inputs(-12, 'felt') == None
    assert 'inputted_data for "felt" cannot be below 0' in caplog.messages


@pytest.mark.parametrize("dmin, expected_value", [
    (12.5, 12.5),
    (5, 5),
    (5235, 5235),
    (0, 0),
    (None, None),
    ('12.5', None),
    (-12, None),
    ('0', None), 
    ('-1', None),  
    ('string', None),  
    (True, None), 
    (False, None), 
    ([], None),
    ({}, None), 
    (set(), None),
    ([12.5], None),
    (0.0, 0.0),
])
def test_validate_dmin(dmin, expected_value):
    assert validate_dmin(dmin) == expected_value


def test_validate_dmin_missing_reading(caplog):
    assert validate_dmin(None) == None
    assert 'No recorded value for "dmin"' in caplog.messages


def test_validate_dmin_wrong_data_type(caplog):
    assert validate_dmin('12') == None
    assert 'Invalid data type: expected int in "dmin"' in caplog.messages


def test_validate_dmin_negative(caplog):
    assert validate_dmin(-5) == None
    assert '"dmin" cannot be below 0' in caplog.messages


@pytest.mark.parametrize("eq_type, eq_type_name, expected_value", [
    ('earthquake', 'earthquake_type', 'earthquake'),
    ('quarry', 'earthquake_type', 'quarry'),
    ('ml', 'magtype', 'ml'),
    ('mww', 'magtype', 'mww'),
    ('mwb', 'magtype', 'mwb'),
    (['ml'], 'magtype', None),
    (['tsunami'], 'earthquake_type', None),
])
def test_validate_types(eq_type, eq_type_name, expected_value):
    assert validate_types(eq_type, eq_type_name) == expected_value


@pytest.mark.parametrize("eq_type, eq_type_name, expected_value", [
    (12, 'magtype', None),
    (['ml'], 'magtype', None),
    ({'type': 'ml'}, 'magtype', None),
    ((1, 'ml'), 'magtype', None),
    (424, 'earthquake_type', None),
    (['quake'], 'earthquake_type', None),
    ({'type': 'earthquake'}, 'earthquake_type', None),
    ((1, 'quake'), 'earthquake_type', None),

])
def test_validate_types_invalid_data_type(eq_type, eq_type_name, expected_value, caplog):
    assert validate_types(eq_type, eq_type_name) == expected_value
    assert f'Invalid data type: expected a string for "{eq_type_name}"' in caplog.messages


@pytest.mark.parametrize("network, expected_value", [
    (12, None),
    ('werewr', None),
    ('uu', 'uu'),
    (['aa'], None),
    (('bbc'), None),
    ({'network': 'uu'}, None),
    ('3', None),
    ('ag', 'ag'),
    ('aeg', None),
])
def test_validate_network(network, expected_value):
    assert validate_network(network) == expected_value


@pytest.mark.parametrize("network, expected_value", [
    (12, None),
    (['ag'], None),
    ((1, 'uu'), None),
    ({'network': 'uu'}, None),
])
def test_validate_network_invalid_data_type(network, expected_value , caplog):
    assert validate_network(network) == expected_value
    assert 'Invalid data type for "network": expected a string' in caplog.messages


@pytest.mark.parametrize("network, expected_value", [
    ('abd', None),
    ('f', None),
])
def test_validate_network_invalid_length(network, expected_value, caplog):
    assert validate_network(network) == expected_value
    assert 'Invalid length for "network": expected 2' in caplog.messages


@pytest.mark.parametrize("value, earthquake_property, expected_value", [
    ('yellow', 'alert', 'yellow'),
    ('red', 'alert', 'red'),
    ('green', 'alert', 'green'),
    ('blue', 'alert', None),
    (['green'], 'alert', None),
    ({'alert': 'green'}, 'alert', None),
    (None, 'alert', None),
    ('automatic', 'status', 'automatic'),
    ('reviewed', 'status', 'reviewed'),
    (['reviewed'], 'status', None),
    ({'status': 'deleted'}, 'status', None),
    (None, 'status', None),
])
def test_validate_property(value, earthquake_property, expected_value):
    assert validate_property(value, earthquake_property) == expected_value


def test_validate_property_none(caplog):
    assert validate_property(None, 'alert') == None
    assert 'No recorded value for "alert"' in caplog.messages


@pytest.mark.parametrize("value, earthquake_property, expected_value", [
    (['reviewed'], 'status', None),
    ({'status': 'deleted'}, 'status', None),
    (['blue'], 'alert', None),
    ({'alert': 'orange'}, 'status', None),
])
def test_validate_property_not_string(value, earthquake_property, expected_value, caplog):
    assert validate_property(value, earthquake_property) == expected_value
    assert f'Invalid data type: expected string for "{earthquake_property}"' in caplog.messages


def test_validate_property_invalid_alert(caplog):
    assert validate_property('blue', 'alert') == None
    assert '"alert" not recognised. Value must be: green, yellow, orange, red' in caplog.messages


def test_validate_property_invalid_status(caplog):
    assert validate_property('done', 'status') == None
    assert '"status" not recognised. Value must be: automatic, reviewed, deleted' in caplog.messages


@pytest.mark.parametrize("reading, reading_type, expected_value", [
    (6.3, 'mag', 6.3),
    (10.0, 'mag', 10.0),
    (-0.20, 'mag', -0.20),
    (-167.2378, 'lon', -167.2378),
    (180.0, 'lon', 180.0),
    (49, 'lat', 49),
    (-20.1, 'lat', -20.1),
    (233, 'depth', 233),
    (2.3, 'cdi', 2.3),
    (6.3, 'mmi', 6.3),
    (0, 'mmi', 0),
    (323, 'sig', 323),
    (96.2, 'gap', 96.2),
    ('10', 'mag', None),
    (190, 'lon', None),
    (91, 'lat', None),
    ('289', 'depth', None),
    (13, 'cdi', None),
    ([3.9], 'mag', None),
    ('invalid', 'sig', None),
    ({'value': 96.2}, 'gap', None),  
    (True, 'mag', None), 
    (False, 'mag', None),
])
def test_validate_reading(reading, reading_type, expected_value):
    assert validate_reading(reading, reading_type) == expected_value


@pytest.mark.parametrize("reading, reading_type, expected_value", [
    (None, 'mag', None),
    (None, 'lon', None),
    (None, 'lat', None),
    (None, 'depth', None),
    (None, 'cdi', None),
    (None, 'mag', None),
])
def test_validate_reading_missing_value(reading, reading_type, expected_value, caplog):
    assert validate_reading(reading, reading_type) == expected_value
    assert f'No recorded value for "{reading_type}"' in caplog.messages


@pytest.mark.parametrize("reading, reading_type, expected_value", [
    ([6.4], 'mag', None),
    ({'sig': 299}, 'sig', None),
    ('33', 'lat', None),
    ((1, 57), 'lon', None),
])
def test_validate_reading_invalid_format(reading, reading_type, expected_value, caplog):
    assert validate_reading(reading, reading_type) == expected_value
    assert f'Invalid data type: expected a number for "{reading_type}"' in caplog.messages


@pytest.mark.parametrize("reading, reading_type, expected_value", [
    (11, 'mag', None),
    (-20, 'mag', None),
    (-197.2378, 'lon', None),
    (180.1, 'lon', None),
    (900, 'lat', None),
    (-220.1, 'lat', None),
    (1223, 'depth', None),
    (13.9, 'cdi', None),
    (-0.01, 'mmi', None),
    (19, 'mmi', None),
    (-1, 'sig', None),
    (361, 'gap', None),
])
def test_validate_reading_invalid_range(reading, reading_type, expected_value, caplog):
    assert validate_reading(reading, reading_type) == expected_value
    expected_message = f'"{reading_type}" value {reading} out of range.'
    assert any(expected_message in message for message in caplog.messages)


def test_clean_data(example_erroneous_reading, get_current_utc_time):
    assert clean_data(get_earthquake_data(example_erroneous_reading)) == {
        'earthquake_id': 'c3820fd332',
        'alert': None,
        'status': 'reviewed',
        'network': 'ci',
        'magtype': 'ml',
        'earthquake_type': 'earthquake',
        'magnitude': 0.67,
        'lon': None,
        'lat': 35.7305,
        'depth': None,
        'time': get_current_utc_time,
        'felt': None,
        'cdi': None,
        'mmi': None,
        'significance': 7,
        'nst': None,
        'dmin': 0.1163,
        'gap': 146,
        'title': 'M 0.7 - 13 km WSW of Searles Valley, CA'
    }


def test_transform_process(example_reading, example_erroneous_reading, get_current_utc_time):
    readings = [example_reading, example_erroneous_reading]
    assert (transform_process(readings)) == [
         {
            'alert': 'red',
            'cdi': 5.6,
            'depth': 1.88,
            'dmin': 0.1163,
            'earthquake_id': 'ci40801680',
            'earthquake_type': 'earthquake',
            'felt': None,
            'gap': 146,
            'lat': 35.7305,
            'lon': -117.542,
            'magnitude': 0.67,
            'magtype': 'ml',
            'mmi': 6.0,
            'network': 'ci',
            'nst': 17,
            'significance': 7,
            'status': 'reviewed',
            'time': '2024/06/18 13:50:56',
            'title': 'M 0.7 - 13 km WSW of Searles Valley, CA',
    },
        {
            'alert': None,
            'cdi': None,
            'depth': None,
            'dmin': 0.1163,
            'earthquake_id': 'c3820fd332',
            'earthquake_type': 'earthquake',
            'felt': None,
            'gap': 146,
            'lat': 35.7305,
            'lon': None,
            'magnitude': 0.67,
            'magtype': 'ml',
            'mmi': None,
            'network': 'ci',
            'nst': None,
            'significance': 7,
            'status': 'reviewed',
            'time': get_current_utc_time,
            'title': 'M 0.7 - 13 km WSW of Searles Valley, CA',
        },
    ]
