from transform import *
import pytest
import logging

@pytest.mark.parametrize("property_name, expected_value", [
    ('mag', 0.67),
    ('time', 1718718656830),
    ('felt', 23),
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
        result = get_earthquake_property(
            example_reading_missing_values, property_name)
        assert result == expected_value
        if expected_value is None:
            assert 'Property non_existent_property not in data' in caplog.messages
        else:
            assert not caplog.messages

def test_get_earthquake_property_missing_data(empty_reading)