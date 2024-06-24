import boto3
from dotenv import load_dotenv
from os import environ as ENV
from haversine import haversine

load_dotenv()


def get_sns_client():
    return boto3.client('sns',
                        aws_access_key_id=ENV.get("ACCESS_KEY"),
                        aws_secret_access_key=ENV.get("SECRET_ACCESS_KEY"))


def calculate_distance(topic_coordinates, earthquake_coordinates):
    """
    Calculates the distance of an earthquake to all topics
    if within a certain distance based of dmin/mag then will
    send notifications to all users subscribed to that topic
    """
    return haversine(topic_coordinates, earthquake_coordinates)



def get_topics():
    """
    Gets topics from database
    """
    ...


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
    ...
