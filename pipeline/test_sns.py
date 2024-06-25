from sns import *

from unittest.mock import patch, MagicMock
import boto3


def mock_env_get(key):
    if key == "ACCESS_KEY":
        return 'fake_access_key'
    elif key == "SECRET_ACCESS_KEY":
        return 'fake_secret_key'
    elif key == "DB_HOST":
        return 'fake_db_host'
    elif key == "DB_NAME":
        return 'fake_db_name'
    elif key == "DB_USERNAME":
        return 'fake_db_username'
    elif key == "DB_PASSWORD":
        return 'fake_db_password'
    elif key == "DB_PORT":
        return 'fake_db_port'


@patch('sns.boto3.client')
@patch('sns.ENV.get', side_effect=mock_env_get)
def test_get_sns_client_success(mock_env_get, mock_boto_client):
    mock_client = MagicMock()
    mock_boto_client.return_value = mock_client

    client = get_sns_client()

    mock_env_get.assert_any_call("ACCESS_KEY")
    mock_env_get.assert_any_call("SECRET_ACCESS_KEY")
    mock_boto_client.assert_called_once_with('sns',
                                             aws_access_key_id='dummy_access_key',
                                             aws_secret_access_key='dummy_secret_key')
    assert client == mock_client


@patch('sns.psycopg2.connect')
@patch('sns.ENV.get', side_effect=mock_env_get)
def test_get_connection(mock_env_get, mock_connection):
    mock_conn = MagicMock()
    mock_connection.return_value = mock_conn

    conn = get_connection()

    mock_env_get.assert_any_call("ACCESS_KEY")
    mock_env_get.assert_any_call("SECRET_ACCESS_KEY")
