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
            assert 'Property non_existent_property not in data' in caplog.messages
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


@pytest.mark.parametrize("name, expected_value", [
    ('M 0.7 - 13 km WSW of Searles Valley, CA', 'M 0.7 - 13 km WSW of Searles Valley, CA'),
    ('ci40801680', 'ci40801680'),
    (12345, None),
    (['ci40801680'], None),
    ({'id': 'ci40801680'}, None),
    ('ak0247tbx02t', 'ak0247tbx02t'),
    ('M 0.9 - 6 km NNW of Houston, Alaska', 'M 0.9 - 6 km NNW of Houston, Alaska'),
    (('M 0.9 - 6 km NNW of Houston, Alaska', 'ak0247tbx02t'), None),
])
def test_validate_earthquake_naming(name, expected_value, caplog):
    with caplog.at_level(logging.ERROR):
        assert validate_earthquake_naming(name) == expected_value
        if expected_value is None:
            assert 'Invalid data type: expected string' in caplog.messages
        else:
            assert not caplog.messages


def test_validate_earthquake_naming_no_value(caplog):
    with caplog.at_level(logging.ERROR):
        assert validate_earthquake_naming(None) == None
        assert 'No recorded value' in caplog.messages


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
    (None, None)

])
def test_validate_time(time_in_ms, expected_value, get_current_utc_time, caplog):
    if expected_value in ['future_date', 'string', 'list', 'dict']:
        expected_value = get_current_utc_time
    assert validate_time(time_in_ms) == expected_value
    if expected_value is None:
        assert 'No recorded value' in caplog.messages


def test_validate_time_invalid_data_type(get_current_utc_time, caplog):
    assert validate_time('error') == get_current_utc_time
    assert 'Invalid data type: expected int for time_in_ms' in caplog.messages


def test_validate_time_future_time(get_current_utc_time, caplog):
    assert validate_time(33109056003843) == get_current_utc_time
    assert 'Future earthquake cannot be predicted' in caplog.messages
