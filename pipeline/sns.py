# pylint: disable=W0718, W1203

"""This script sends sns alerts to interested users"""

from os import environ as ENV
import logging
import boto3
from dotenv import load_dotenv
from haversine import haversine
from psycopg2.extensions import connection, cursor
import psycopg2.extras

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


def calculate_distance(coordinate_1: tuple, coordinate_2: tuple) -> int | None:
    """
    Calculates the distance in km between 2 coordinates
    """
    try:
        return int(haversine(
            coordinate_1, coordinate_2))
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

def get_notification_distance(magnitude):
    if not isinstance(magnitude, (int, float)):
        return None
    if 4 > magnitude:
        return 50
    if 5 > magnitude > 4:
        return 150
    if magnitude > 5:
        return 200


def check_topic_range(eq_lon: str, eq_lat: str, topic: dict, magnitude: float) -> bool:
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

        return (distance is not None and distance <= get_notification_distance(magnitude))

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
            'min_magnitude': user['min_magnitude'],
            'lon': user['lon'],
            'lat': user['lat']
        }
    except Exception as e:
        logging.error(
            f"An unexpected error occurred getting user information: {e}")
        return {}


def find_related_topics(earthquake: dict, topics) -> list:
    """
    Finds all topics which will be interested in the most recent
    earthquake
    """
    try:
        related_topics = []
        for topic in topics:
            if earthquake['magnitude'] >= topic['min_magnitude'] and \
                    check_topic_range(earthquake['lon'], earthquake['lat'], topic, earthquake['magnitude']):
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
                SELECT uta.user_id, u.email_address, u.phone_number, t.topic_arn, t.min_magnitude, t.lat, t.lon
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
    for earthquake in earthquakes:
        related_topics = find_related_topics(earthquake, topics)
        subscribed_users = get_subscribed_users(conn, related_topics)
        for user in subscribed_users:
            magnitude = earthquake['magnitude']
            eq_coordinates = (earthquake['lon'], earthquake['lat'])
            topic_coordinates = (user['lon'], user['lat'])
            distance = calculate_distance(topic_coordinates, eq_coordinates)
            message = (
f"""

**EARTHQUAKE WARNING!**

A magnitude {magnitude} or above earthquake has been detected within {distance}km of your area.

SAFETY TIPS:

1. DROP, COVER, and HOLD ON: Drop to your hands and knees. Take cover under a sturdy table or desk, or cover your head and neck with your arms. Hold on until the shaking stops.

2. STAY INDOORS: Remain inside; do not run outside while the building is shaking.

3. AVOID WINDOWS AND HEAVY OBJECTS: Move away from windows, glass, and any objects that could fall, like bookcases or mirrors.

4. IF OUTSIDE, FIND AN OPEN AREA: Move to a clear area away from buildings, trees, streetlights, and wires.

5. IF IN A CAR, PULL OVER SAFELY: Pull over to a safe location and stay inside until the shaking stops.

Stay safe and follow these guidelines until the shaking subsides.
"""
            )
            subject = "EARTHQUAKE WARNING"
            send_message(
                sns_client, user['topic_arn'], subject, message
            )


if __name__ == "__main__":
    import extract
    import transform
    example_data = [{
        "earthquake_id": "ak0247tc2ogk",
        "alert": "green",
        "status": "automatic",
        "network": "ak",
        "magtype": "ml",
        "earthquake_type": "earthquake",
        "magnitude": 6.0,
        "lon": -2.964996,
        "lat": 53.508624,
        "depth": 0,
        "time": '2024-06-24 12: 22: 22',
        "felt": None,
        "cdi": None,
        "mmi": None,
        "significance": 158,
        "nst": None,
        "dmin": None,
        "gap": None,
        "title": "M 3.2 - 88 km NW of Yakutat, Alaska"
    }]
    # extract_data = extract.extract_process()
    # transform_data = transform.transform_process(extract_data)
    # if transform_data:
    #     sns_alert_system(transform_data)
    sns_alert_system(example_data)