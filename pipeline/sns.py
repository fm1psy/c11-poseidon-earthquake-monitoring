# pylint: disable=W0718, W1203

"""This script sends sns alerts to interested users"""

from os import environ as ENV
import logging
import boto3
from dotenv import load_dotenv
from haversine import haversine
from psycopg2.extensions import connection, cursor
import psycopg2.extras



NOTIFICATION_RADIUS = 10

load_dotenv()

def get_sns_client():
    """
    Gets connection to the boto3 sns client
    """
    try:
        return boto3.client('sns',
                                aws_access_key_id=ENV.get("ACCESS_KEY"),
                                aws_secret_access_key=ENV.get("SECRET_ACCESS_KEY"))
    except Exception as e:
        logging.error(
            f"An unexpected error occurred in getting sns client: {e}")
        return None


def get_connection() -> connection:
    """
    Creates a psycopg2 connection
    """
    try:
        return psycopg2.connect(host=ENV.get('DB_HOST'),
                                database=ENV.get('DB_NAME'),
                                user=ENV.get('DB_USERNAME'),
                                password=ENV.get('DB_PASSWORD'),
                                port=ENV.get('DB_PORT'))
    except Exception as e:
        logging.error(
            f"An unexpected error occurred in getting connection: {e}")
        return None


def get_cursor(conn: connection) -> cursor:
    """
    Creates a cursor based on provided psycopg2 connection
    """
    try:
        return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    except Exception as e:
        logging.error(
            f"An unexpected error occurred in getting cursor: {e}")
        return None


def calculate_distance(topic_coordinates: tuple, earthquake_coordinates: tuple) -> int | None:
    """
    Calculates the distance in km between 2 coordinates
    """
    try:
        return int(haversine(
            topic_coordinates, earthquake_coordinates))
    except (TypeError, ValueError) as e:
        logging.error(f"Error calculating distance: {e}")
        return None

def get_topics(conn: connection)-> list[dict]:
    """
    Gets all topics from database
    """
    try:
        with get_cursor(conn) as cur:
            query = """SELECT * FROM topics;"""
            cur.execute(query)
            topic_coordinates = cur.fetchall()
        return topic_coordinates
    except Exception as e:
        logging.error(f"Error fetching topics: {e}")
        return []


def get_topic_detail(topic: dict, detail: str) -> str | None:
    """
    A function which will be used to fetch: 
    topic_arn, longitude, latitude, min_magnitude
    """
    try:
        return topic[detail]
    except Exception as e:
        logging.error(f"Error getting topic details: {e}")
        return None


def check_topic_range(eq_lon: str, eq_lat: str, topic: dict) -> bool:
    """
    Checks to see if the topic location is within 10km of
    the most recent earthquake
    """
    try:
        topic_lat = float(get_topic_detail(topic, 'lat'))
        topic_lon = float(get_topic_detail(topic, 'lon'))
        topic_coordinates = (topic_lat, topic_lon)
        earthquake_coordinates = (eq_lat, eq_lon)

        distance = calculate_distance(
            topic_coordinates, earthquake_coordinates)

        return (distance is not None and distance <= NOTIFICATION_RADIUS)

    except Exception as e:
        logging.error(
            f"An unexpected error occurred getting topic distance to earthquake: {e}")
        return False


def get_user_information(user: dict) -> dict:
    """
    Gets the user information from users
    """
    try:
        return {
            'user_id': user['user_id'],
            'email_address': user['email_address'],
            'phone_number': user['phone_number'],
            'topic_arn': user['topic_arn'],
            'min_magnitude': user['min_magnitude']
        }
    except Exception as e:
        logging.error(
            f"An unexpected error occurred getting user information: {e}")
        return {}


def find_related_topics(latest_earthquakes: list[dict], topics) -> list:
    """
    Finds all topics which will be interested in the most recent
    earthquake
    """
    try:
        related_topics = []
        for earthquakes in latest_earthquakes:
            for topic in topics:
                if earthquakes['magnitude'] >= topic['min_magnitude'] and \
                    check_topic_range(earthquakes['lon'], earthquakes['lat'], topic):
                    related_topics.append(topic)
        return related_topics
    except Exception as e:
        logging.error(
            f"An unexpected error occurred getting related topics: {e}")
        return []

def get_subscribed_users(conn: connection, related_topics: list) -> list:
    """
    Gets all user details for users who have subscribed to interested 
    topics
    """
    try:
        with get_cursor(conn) as cur:
            for topic in related_topics:
                query = """
                SELECT uta.user_id, u.email_address, u.phone_number, t.topic_arn, t.min_magnitude
                FROM user_topic_assignments AS uta
                JOIN users AS u ON u.user_id = uta.user_id
                JOIN topics AS t ON uta.topic_id = t.topic_id
                WHERE uta.topic_id = %s;
                """
                cur.execute(query, (topic['topic_id'],))
                rows = cur.fetchall()
                return [get_user_information(row) for row in rows]
    except Exception as e:
        logging.error(
            f"An unexpected error occurred getting subscribed users: {e}")
        return []


def send_message(sns_client: boto3.client, arn: str, subject: str, message: str):
    """
    Publishes a message to all subscribers of a topic via SNS
    """
    try:
        sns_client.publish(
            TargetArn=arn,
            Message=message,
            Subject=subject
        )
    except Exception as e:
        logging.error(
            f"An unexpected error occurred when sending messages: {e}")


def sns_alert_system(earthquakes: list[dict]):
    """
    This is the main function which runs through the functions to
    get all users interested in relevant earthquakes, and sends a
    message to all interested users.
    """
    sns_client = get_sns_client()
    conn = get_connection()

    topics = get_topics(conn)
    related_topics = find_related_topics(earthquakes, topics)
    subscribed_users = get_subscribed_users(conn, related_topics)

    for user in subscribed_users:
        magnitude = user['min_magnitude']
        message = (
            f"Earthquake Alert! Magnitude {magnitude} or above "
            "earthquake detected in your area"
        )
        subject = "Earthquake Alert"
        send_message(
            sns_client, user['topic_arn'], subject, message
        )


if __name__ == "__main__":
    import extract
    import transform

    extract_data = extract.extract_process()
    transform_data = transform.transform_process(extract_data)
    if transform_data:
        sns_alert_system(transform_data)
