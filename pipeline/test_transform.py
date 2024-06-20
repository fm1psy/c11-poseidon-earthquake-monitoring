from transform import *
import pytest
import logging

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
