from sns import *

from unittest.mock import patch, MagicMock
import boto3
import pytest

def mock_env_get(key):
    if key == "ACCESS_KEY":
        return 'fake_access_key'
    elif key == "SECRET_ACCESS_KEY":
        return 'fake_secret_key'
    elif key == "DB_HOST":
        return 'fake_host'
    elif key == "DB_NAME":
        return 'fake_name'
    elif key == "DB_USERNAME":
        return 'fake_username'
    elif key == "DB_PASSWORD":
        return 'fake_password'
    elif key == "DB_PORT":
        return 'fake_port'


@patch('sns.boto3.client')
@patch('sns.ENV.get', side_effect=mock_env_get)
def test_get_sns_client_success(mock_env_get, mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client

    client = get_sns_client()

    mock_env_get.assert_any_call("ACCESS_KEY")
    mock_env_get.assert_any_call("SECRET_ACCESS_KEY")
    mock_boto_client.assert_called_once_with('sns',
                                             aws_access_key_id='fake_access_key',
                                             aws_secret_access_key='fake_secret_key')
    assert client == mock_client


@patch('sns.psycopg2.connect')
@patch('sns.ENV.get', side_effect=mock_env_get)
def test_get_connection(mock_env_get, mock_connection):
    mock_conn = MagicMock()
    mock_connection.return_value = mock_conn

    conn = get_connection()

    mock_env_get.assert_any_call("DB_HOST")
    mock_env_get.assert_any_call("DB_NAME")
    mock_env_get.assert_any_call("DB_USERNAME")
    mock_env_get.assert_any_call("DB_PASSWORD")
    mock_env_get.assert_any_call("DB_PORT")
    mock_connection.assert_called_once_with(host='fake_host',
                                            database='fake_name',
                                            user='fake_username',
                                            password='fake_password',
                                            port='fake_port')


    assert conn == mock_conn


@patch('sns.psycopg2.connect')
def test_get_cursor(mock_connect):
    mock_conn = MagicMock(spec=connection)
    mock_cursor = MagicMock(spec=psycopg2.extensions.cursor)
    mock_cursor_factory = MagicMock(spec=psycopg2.extras.RealDictCursor)
    mock_conn.cursor.return_value = mock_cursor


    psycopg2.extras.RealDictCursor = mock_cursor_factory

    cursor = get_cursor(mock_conn)

    mock_conn.cursor.assert_called_once_with(
        cursor_factory=psycopg2.extras.RealDictCursor)
    assert cursor == mock_cursor


@pytest.mark.parametrize("location_1, location_2, expected_value", 
    ([
        ((40.7128, -74.0060), (51.5074, -0.1278), 5570), 
        ((48.8566, 2.3522), (55.7558, 37.6176), 2486), 
        ((34.0522, -118.2437), (19.4326, -99.1332), 2490), 
        ((35.6895, 139.6917), (37.7749, -122.4194), 8270), 
        ((55.7558, 37.6176), (55.6761, 12.5683), 1560), 
        ((51.5074, -0.1278), (41.9028, 12.4964), 1433),
        ((19.4326, -99.1332), (-33.4489, -70.6693), 6610),
        ((37.7749, -122.4194), (-33.8688, 151.2093), 11947),
        ((40.7128, -74.0060), (39.9042, 116.4074), 10989),
        ((35.6895, 139.6917), (22.3193, 114.1694), 2879)
    ]))
def test_calculate_distance(location_1, location_2, expected_value):
    assert calculate_distance(location_1, location_2) == expected_value


def test_get_topics_success():

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

    mock_topic_data = [('Topic 1', 'Description 1'),
                       ('Topic 2', 'Description 2')]
    mock_cursor.fetchall.return_value = mock_topic_data


    topic_coordinates = get_topics(mock_conn)

    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with("SELECT * FROM topics;")
    assert topic_coordinates == mock_topic_data


@pytest.mark.parametrize("topic, detail, expected_result", [
    ({'topic_arn': 'arn:aws:sns:us-east-1:123456789012:MyTopic'},
     'topic_arn', 'arn:aws:sns:us-east-1:123456789012:MyTopic'),
    ({'lon': '-74.0060'}, 'lon','-74.0060'),
    ({'lat': '40.7128'}, 'lat', '40.7128'),
    ({'min_magnitude': '5.0'}, 'min_magnitude', '5.0')
])
def test_get_topic_detail(topic, detail, expected_result):
    assert get_topic_detail(topic, detail) == expected_result


def test_check_topic_in_range(liverpool_earthquake, example_topic):
    lon = liverpool_earthquake[0]['lon']
    lat = liverpool_earthquake[0]['lat']
    assert check_topics_in_range(lon, lat, example_topic) == True


def test_check_topic_not_in_range(example_transformed_data, example_topic):
    lon = example_transformed_data[0]['lon']
    lat = example_transformed_data[0]['lat']
    assert check_topics_in_range(lon, lat, example_topic) == False



@pytest.mark.parametrize("detail, expected_result", [
    ('user_id', 22),
    ('email_address', 'trainee.joe.lam@sigmalabs.co.uk'),
    ('phone_number', '447482569206'),
    ('topic_arn', 'arn:aws:sns:eu-west-2:129033205317:c11-poseidon-test_email'),
    ('min_magnitude', 4.5)
])
def test_get_user_information(detail, expected_result, example_user):
    assert get_user_information(example_user)[detail] == expected_result


def test_get_subscribed_users(example_users, example_topics):
    conn = MagicMock()
    cursor = MagicMock()
    conn.cursor.return_value.__enter__.return_value = cursor
    cursor.execute.return_value = example_users
    cursor.fetchall.return_value = example_users
    assert get_subscribed_users(conn, example_topics) == [{'user_id': 22, 'email_address': 'trainee.joe.lam@sigmalabs.co.uk', 'phone_number': '447482569206', 'topic_arn': 'arn:aws:sns:eu-west-2:129033205317:c11-poseidon-test_email', 'min_magnitude': 4.5}, {
        'user_id': 21, 'email_address': 'trainee.ella.jepsen@sigmalabs.co.uk', 'phone_number': '07552224539', 'topic_arn': 'arn:aws:sns:eu-west-2:129033205317:c11-poseidon-test', 'min_magnitude': 3}]


def test_find_related_topics(liverpool_earthquake, example_topics):
    assert find_related_topics(liverpool_earthquake, example_topics) == [
        {'topic_id': 12, 'topic_arn': 'arn:aws:sns:eu-west-2:129033205317:c11-poseidon-test_email', 'min_magnitude': 4.5, 'lon': -2.964996, 'lat': 53.407624}]
