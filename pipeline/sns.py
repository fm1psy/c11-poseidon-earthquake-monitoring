import boto3
from dotenv import load_dotenv
from os import environ as ENV
from haversine import haversine
import logging
from psycopg2.extensions import connection, cursor
from psycopg2 import OperationalError
import psycopg2.extras


load_dotenv()

def get_sns_client():
    return boto3.client('sns',
                        aws_access_key_id=ENV.get("ACCESS_KEY"),
                        aws_secret_access_key=ENV.get("SECRET_ACCESS_KEY"))


def get_connection() -> connection:
    """Creates a psycopg2 connection"""
    try:
        conn = psycopg2.connect(DB_HOST=ENV.get('DB_HOST')
                                DB_NAME=ENV.get('DB_NAME')
                                DB_USERNAME=ENV.get('DB_USERNAME')
                                DB_PASSWORD=ENV.get('DB_PASSWORD')
                                DB_PORT=ENV.get('DB_PORT'))
        logging.info("Connection established successfully")
        return conn
    except OperationalError as e:
        logging.error(
            f"OperationalError occurred while trying to connect to the database: {e}")
        return None
    except Exception as e:
        logging.error(
            f"An unexpected error occurred in establishing connection: {e}")
        return None


def get_cursor(conn: connection) -> cursor:
    """Creates a cursor based on provided psycopg2 connection"""
    logging.info("Creating a cursor from the psycopg2 connection")
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        logging.info("Cursor created successfully")
        return cursor
    except OperationalError as e:
        logging.error(
            f"OperationalError occurred while trying to create a cursor: {e}")
        return None
    except Exception as e:
        logging.error(
            f"An unexpected error occurred in creating a cursor: {e}")
        return None
    

def calculate_distance(topic_coordinates, earthquake_coordinates):
    """
    Calculates the distance of an earthquake to all topics
    if within a certain distance based of dmin/mag then will
    send notifications to all users subscribed to that topic
    """
    return haversine(topic_coordinates, earthquake_coordinates)



def get_topics(conn):
    """
    Gets topics from database
    """
    cur = get_cursor(conn)

    query = 


def get_topic_details():
    """
    A function should be enough to fetch: topic_arn, longitude, latitude, min_magnitude
    for other functions in the script to determine who to send alerts to
    """
    ...


def get_subscribed_users():
    """
    Find a way to get all users who have subscribed to the mailing list for targeted
    topics
    """
    ...


def send_message(client):
    """
    Creates the alert message. Still work in progress
    """
    client.publish(
        TopicArn=TOPIC,
        Message=" WASSUP",
        Subject="if u get a text can u let me know",
    )


def subscribe(client, email):
    """
    This probably wont stay on this script, may need to send to Ella so 
    new users can get the subscription email
    """
    client.subscribe(
        TopicArn=TOPIC,
        Protocol='email',
        Endpoint=email,
        ReturnSubscriptionArn=True
    )


if __name__ == "__main__":
    client = get_sns_client()
    conn = get_connection
