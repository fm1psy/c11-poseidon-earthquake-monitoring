import boto3
from dotenv import load_dotenv
from os import environ as ENV
from haversine import haversine
import logging
from psycopg2.extensions import connection, cursor
from psycopg2 import OperationalError
import psycopg2.extras
import os

load_dotenv()

def get_sns_client():
    return boto3.client('sns',
                        aws_access_key_id=ENV.get("ACCESS_KEY"),
                        aws_secret_access_key=ENV.get("SECRET_ACCESS_KEY"))


def get_connection() -> connection:
    """Creates a psycopg2 connection"""
    try:
        conn = psycopg2.connect(host=ENV.get('DB_HOST'),
                                database=ENV.get('DB_NAME'),
                                user=ENV.get('DB_USERNAME'),
                                password=ENV.get('DB_PASSWORD'),
                                port=ENV.get('DB_PORT'))
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
    with conn.cursor() as cur:
        query = """SELECT * FROM topics;"""
        cur.execute(query)
        topic_coordinates = cur.fetchall()
    return topic_coordinates


def get_topic_detail(topic, detail):
    """
    A function  to fetch: topic_arn, longitude, latitude, min_magnitude
    """
    return topic[detail]
    

def check_topics_in_range(eq_lon, eq_lat, topics):
    related_topics = []
    for topic in topics:
        topic_lat = get_topic_detail(topic, 'lat')
        topic_lon = get_topic_detail(topic, 'lon')
        topic_coordinates = (topic_lat, topic_lon)
        earthquake_coordinates = (eq_lat, eq_lon)
        if calculate_distance(earthquake_coordinates, topic_coordinates) <= 50:
            related_topics.append(get_topic_detail(topic, 'topic_id'))
    return related_topics


def get_subscribed_users(conn, related_topics):
    """
    Find a way to get all users who have subscribed to the mailing list for targeted
    topics.
    """
    interested_users = []

    with conn.cursor() as cur:
        for topic in related_topics:
            query = """
            SELECT uta.user_id, u.email_address, u.phone_number, u.sms_subscription_arn, u.email_subscription_arn
            FROM user_topic_assignments AS uta
            JOIN users AS u ON u.user_id = uta.user_id
            WHERE uta.topic_id = %s;
            """
            cur.execute(query, (topic,))
            rows = cur.fetchall()

            for row in rows:
                user = {
                    'user_id': row[0],
                    'email_address': row[1],
                    'phone_number': row[2],
                    'sms_subscription_arn': row[3],
                    'email_subscription_arn': row[4]
                }
                if user not in interested_users:  # Avoid duplicates
                    interested_users.append(user)

    return interested_users


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
    conn = get_connection()
    topics = get_topics(conn)
    print(topics)
    related_topics = check_topics_in_range(topics, eq_lon=None, eq_lat=None)
    subscribed_users = get_subscribed_users(conn, related_topics)