import boto3
from dotenv import load_dotenv
from os import environ as ENV
from haversine import haversine
import logging
from psycopg2.extensions import connection, cursor
import psycopg2.extras

example_data = [{
    "earthquake_id": "ak0247tc2ogk",
    "alert": "green",
    "status": "automatic",
    "network": "ak",
    "magtype": "ml",
    "earthquake_type": "earthquake",
    "magnitude": 6.0,
    "lon": -2.964996,
    "lat": 53.407624,
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


load_dotenv()

def get_sns_client():
    try:
        return boto3.client('sns',
                            aws_access_key_id=ENV.get("ACCESS_KEY"),
                            aws_secret_access_key=ENV.get("SECRET_ACCESS_KEY"))

    except Exception as e:
        logging.error(
            f"An unexpected error occurred in establishing sns client: {e}")
        return None
    

def get_connection() -> connection:
    """Creates a psycopg2 connection"""
    try:
        return psycopg2.connect(host=ENV.get('DB_HOST'),
                                database=ENV.get('DB_NAME'),
                                user=ENV.get('DB_USERNAME'),
                                password=ENV.get('DB_PASSWORD'),
                                port=ENV.get('DB_PORT'))
    except Exception as e:
        logging.error(
            f"An unexpected error occurred in establishing connection: {e}")
        return None


def get_cursor(conn: connection) -> cursor:
    """Creates a cursor based on provided psycopg2 connection"""
    try:
        return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
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
    return int(haversine(topic_coordinates, earthquake_coordinates))


def get_topics(conn):
    """
    Gets topics from database
    """
    cursor = get_cursor(conn)
    with cursor as cur:
        query = """SELECT * FROM topics;"""
        cur.execute(query)
        topic_coordinates = cur.fetchall()
    return topic_coordinates


def get_topic_detail(topic, detail):
    """
    A function  to fetch: topic_arn, longitude, latitude, min_magnitude
    """
    return topic[detail]
    

def check_topics_in_range(eq_lon, eq_lat, topic):
    topic_lat = get_topic_detail(topic, 'lat')
    topic_lon = get_topic_detail(topic, 'lon')
    topic_coordinates = (topic_lat, topic_lon)
    earthquake_coordinates = (eq_lat, eq_lon)
    if calculate_distance(earthquake_coordinates, topic_coordinates) <= 50:
        return True
    return False


def get_user_information(user):
    return {
        'user_id': user['user_id'],
        'email_address': user['email_address'],
        'phone_number': user['phone_number'],
        'topic_arn': user['topic_arn'],
        'min_magnitude': user['min_magnitude']
    }


def get_subscribed_users(conn, related_topics):
    """
    Find a way to get all users who have subscribed to the mailing list for targeted
    topics.
    """
    cursor = get_cursor(conn)
    with cursor as cur:
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



def find_related_topics(latest_earthquakes, topics):
    related_topics = []
    for earthquakes in latest_earthquakes:
        for topic in topics:
            if earthquakes['magnitude'] >= topic['min_magnitude'] and check_topics_in_range(earthquakes['lon'], earthquakes['lat'], topic):
                related_topics.append(topic)
    return related_topics


def send_message(sns_client, arn, subject, message):
    """Publishes an email message via SNS"""
    sns_client.publish(
        TargetArn=arn,
        Message=message,
        Subject=subject
    )

def send_text(sns_client, phone_number, message):
    sns_client.publish(
            PhoneNumber=phone_number,
            Message=message
        )

def sns_alert_system(earthquakes):
    sns_client = get_sns_client()
    conn = get_connection()

    topics = get_topics(conn)
    related_topics = find_related_topics(earthquakes, topics)
    subscribed_users = get_subscribed_users(conn, related_topics)

    for user in subscribed_users:
        message = f"Earthquake Alert! Magnitude {user['min_magnitude']} or above earthquake detected in your area"
        subject = "Earthquake Alert"
        send_text(sns_client, user['phone_number'], message)
        send_message(
            sns_client, user['topic_arn'], subject, message)
        

if __name__ == "__main__":
    import extract
    import transform

    extract_data = extract.extract_process()
    transform_data = transform.transform_process(extract_data)

    sns_alert_system(example_data)
