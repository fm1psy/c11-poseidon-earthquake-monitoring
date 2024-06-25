import streamlit as st
from streamlit_folium import st_folium
import folium
import boto3
from os import environ
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection, cursor
import psycopg2.extras

DEFAULT_LAT = 51.5072
DEFAULT_LON = 0.1276


def get_connection():
    return psycopg2.connect(host=environ['DB_HOST'],
                            dbname=environ['DB_NAME'],
                            user=environ['DB_USERNAME'],
                            password=environ['DB_PASSWORD'],
                            port=environ['DB_PORT'])


def get_sns_client():
    load_dotenv()
    return boto3.client(
        'sns',
        aws_access_key_id=environ['ACCESS_KEY'],
        aws_secret_access_key=environ['SECRET_ACCESS_KEY'])


def create_topic(client, user_info):
    response = client.create_topic(
        Name=f"c1""1-poseidon-test"""
    )
    return response


def subscribe_to_topic(client, topic_ARN, user_info):
    email_response = client.subscribe(
        TopicArn=topic_ARN,
        Protocol='email',
        Endpoint=user_info['email']
    )
    sms_response = client.subscribe(
        TopicArn=topic_ARN,
        Protocol='sms',
        Endpoint=user_info['phone_number']
    )
    return email_response, sms_response


def check_if_topic_exists(conn, user_info):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute(f"""select topic_id, topic_arn from topics
                            where min_magnitude='{user_info['magnitude']}' and lon='{user_info['selected_lon']}' and lat='{user_info['selected_lat']}';""")
        result = cursor.fetchall()
    if len(result) == 1:
        return result
    return None


def upload_user_to_database(conn, user_info):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute(f"""insert into users (email_address, phone_number) values (%s, %s) returning user_id;""", (
            user_info['email'], user_info['phone_number']))
        return cursor.fetchone()['user_id']


def check_if_user_exists(conn, user_info):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute(f"""select user_id from users
                            where email_address = '{user_info['email']}' and phone_number = '{user_info['phone_number']}';""")
        result = cursor.fetchall()
    if len(result) == 1:
        return result
    return None


def upload_topic_to_database(conn, user_info, topic_info):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute(f"""insert into topics (topic_arn, min_magnitude, lon, lat) values (%s, %s, %s, %s) returning topic_id;""", (topic_info['TopicArn'],
                                                                                                                                    user_info['magnitude'], user_info['selected_lon'], user_info['selected_lat']))
        return cursor.fetchone()['topic_id']


def upload_user_subscription_to_database(conn, user_id, topic_id, email_subscription, sms_subscription):
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
        cursor.execute(f"""insert into user_topic_assignments (user_id, topic_id, email_subscription_arn, sms_subscription_arn) values (%s, %s, %s, %s);""", (user_id,
                       topic_id, email_subscription['SubscriptionArn'], sms_subscription['SubscriptionArn']))


def unsubscribe_to_topic(client, conn, user_info):
    if check_if_user_exists(conn, user_info):
        response = client.unsubscribe()


def create_subscription_form():
    email = ""
    phone_number = ""
    m = folium.Map(location=[DEFAULT_LAT, DEFAULT_LON], zoom_start=10)
    m.add_child(folium.ClickForMarker())
    m.add_child(folium.LatLngPopup())

    with st.form("notification-subscription", clear_on_submit=True, border=True):
        st.header("Subscribe for earthquake notifications")
        email = st.text_input("Email:")
        phone_number = st.text_input("Phone Number:")
        magnitude = st.selectbox(
            'What is the minimum magnitude of earthquake that you would like to be notified of?',
            ('0 - All earthquakes', '1 - rlly small', '2 - micro', '3 - minor',
             '4 - light', '5 - moderate', '6 - strong', '7 - major', '8 - great')
        )
        map = st_folium(m)

        if map.get("last_clicked"):
            selected_lat = map["last_clicked"]["lat"]
            selected_lon = map['last_clicked']['lng']

        submit = st.form_submit_button()

    if submit and email and magnitude and phone_number and selected_lat and selected_lon:
        st.success(f"""Email entered: {email}, Phone Number entered: {
            phone_number}, Position Chosen: {selected_lat}, {selected_lon}, Minimum magnitude chosen: {magnitude}""")

        return {'email': email, 'phone_number': phone_number, 'selected_lat': selected_lat, 'selected_lon': selected_lon, 'magnitude': magnitude.split(" ")[0]}
    return []


if __name__ == "__main__":
    user_info = create_subscription_form()
    if user_info != []:
        client = get_sns_client()
        conn = get_connection()
        if check_if_user_exists(conn, user_info) is None:
            user_id = upload_user_to_database(conn, user_info)
        if check_if_topic_exists(conn, user_info) is None:
            topic_info = create_topic(client, user_info)
            topic_id = upload_topic_to_database(conn, user_info, topic_info)
        email_subscription, sms_subscription = subscribe_to_topic(
            client, topic_info['TopicArn'], user_info)
        upload_user_subscription_to_database(
            conn, user_id, topic_id, email_subscription, sms_subscription)
        conn.commit()
