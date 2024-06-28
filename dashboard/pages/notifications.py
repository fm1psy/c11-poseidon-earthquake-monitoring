"""create the notification subscription page for the dashboard"""
from os import environ
import streamlit as st
from streamlit_folium import st_folium
import folium
import boto3
from dotenv import load_dotenv
import psycopg2
import psycopg2.extras

DEFAULT_LAT = 51.5072
DEFAULT_LON = 0.1276


def get_connection():
    """gets connnection to database"""
    return psycopg2.connect(host=environ['DB_HOST'],
                            dbname=environ['DB_NAME'],
                            user=environ['DB_USERNAME'],
                            password=environ['DB_PASSWORD'],
                            port=environ['DB_PORT'])


def get_sns_client():
    """returns sns client"""
    load_dotenv()
    return boto3.client(
        'sns',
        aws_access_key_id=environ['AWS_ACCESS_KEY'],
        aws_secret_access_key=environ['AWS_SECRET_KEY'],
        region_name='eu-west-2')


def create_topic(client):
    """creates sns topic for particular longitude, latitude and magnitude"""
    response = client.create_topic(
        Name="c11-poseidon-test"
    )
    return response


def subscribe_to_topic(client, topic_arn, user_info):
    """subscribes a user to a given topic"""
    email_response = client.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=user_info['email']
    )
    sms_response = client.subscribe(
        TopicArn=topic_arn,
        Protocol='sms',
        Endpoint=user_info['phone_number']
    )
    return email_response, sms_response


def check_if_topic_exists(conn, user_info):
    """checks if given topic already exists"""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curr:
        curr.execute(f"""select topic_id, topic_arn from topics
                            where min_magnitude='{user_info['magnitude']}'
                            and lon='{user_info['selected_lon']}'
                            and lat='{user_info['selected_lat']}';""")
        result = curr.fetchall()
    if len(result) == 1:
        return result
    return None


def upload_user_to_database(conn, user_info):
    """uploads new user to the user table in database"""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curr:
        curr.execute("""insert into users (email_address, phone_number)
                       values (%s, %s) returning user_id;""", (
            user_info['email'], user_info['phone_number']))
        return curr.fetchone()['user_id']


def check_if_user_exists(conn, user_info):
    """checks if given user already exists"""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curr:
        curr.execute(f"""select user_id from users
                            where email_address = '{user_info['email']}'
                            and phone_number = '{user_info['phone_number']}';""")
        result = curr.fetchall()
    if len(result) == 1:
        return result
    return None


def upload_topic_to_database(conn, user_info, topic_info):
    """uploads new topic to topics table in database"""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curr:
        curr.execute("""insert into topics (topic_arn, min_magnitude, lon, lat)
                       values (%s, %s, %s, %s)
                       returning topic_id;""", (topic_info['TopicArn'],
                                                user_info['magnitude'],
                                                user_info['selected_lon'],
                                                user_info['selected_lat']))
        return curr.fetchone()['topic_id']


def upload_user_subscription_to_database(conn, user_id, topic_id,
                                         email_subscription, sms_subscription):
    """uploads user_id, topic_id, email_subscription_arn and sms_subscription_arn 
        to user_topic_assignments table in database"""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curr:
        curr.execute("""insert into user_topic_assignments
                       (user_id, topic_id, email_subscription_arn, sms_subscription_arn)
                       values (%s, %s, %s, %s);""", (user_id,
                                                     topic_id,
                                                     email_subscription['SubscriptionArn'],
                                                     sms_subscription['SubscriptionArn']))


def create_subscription_form():
    """creates notification subscription form"""
    email = ""
    phone_number = ""
    m = folium.Map(location=[DEFAULT_LAT, DEFAULT_LON],
                   zoom_start=10)
    m.add_child(folium.ClickForMarker())
    m.add_child(folium.LatLngPopup())

    with st.form("notification-subscription", clear_on_submit=True, border=True):
        st.header("Subscribe for Earthquake Notifications")
        email = st.text_input("Email:")
        phone_number = st.text_input("Phone Number:")
        magnitude = st.selectbox(
            'What is the minimum magnitude of earthquake that you would like to be notified of?',
            ('0 - All earthquakes', '1 - rlly small', '2 - micro', '3 - minor',
             '4 - light', '5 - moderate', '6 - strong', '7 - major', '8+ - great')
        )
        st.write(
            "Click on the map below to choose location that you would like to be notified about")
        world_map = st_folium(m, width=900, height=500)

        if world_map.get("last_clicked"):
            selected_lat = world_map["last_clicked"]["lat"]
            selected_lon = world_map['last_clicked']['lng']

        submit = st.form_submit_button()

    if submit and email and magnitude and phone_number and selected_lat and selected_lon:
        st.success(f"""Email entered: {email},
                Phone Number entered: {phone_number},
                Position Chosen: {selected_lat}, {selected_lon},
                Minimum magnitude chosen: {magnitude}""")

        return {'email': email, 'phone_number': phone_number,
                'selected_lat': selected_lat, 'selected_lon': selected_lon,
                'magnitude': magnitude.split(" ")[0]}
    return []


def unsubscribe_user_from_topic(client, email_subscription_arn, sms_subscription_arn):
    """unsubscribes given user from topic that matches the given email and sms subscription arns"""
    client.unsubscribe(
        SubscriptionArn=sms_subscription_arn
    )
    client.unsubscribe(
        SubscriptionArn=email_subscription_arn
    )


def get_user_subscription_arn(conn, user_info):
    """returns a given users email and sms subscription arns"""
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curr:
        curr.execute(f"""select uta.sms_subscription_arn, uta.email_subscription_arn
                            from user_topic_assignments as uta
                            join users as u on u.user_id = uta.user_id
                            where u.email_address = '{user_info['email_address']}'
                            and u.phone_number = '{user_info['phone_number']}'""")
        result = curr.fetchone()
    return result["sms_subscription_arn"], result["email_subscription_arn"]


def create_unsubscribe_form():
    """creates unsubscribe form"""
    email = ""
    phone_number = ""
    with st.form("notification-unsubscribe", clear_on_submit=True, border=True):
        st.header("Unsubscribe from earthquake notifications")
        st.write("""If you have previously subscribed to receiving earthquake notifications and wish to unsubscribe,
                 please enter the email and phone number used when subscribing below:""")
        email = st.text_input("Email:")
        phone_number = st.text_input("Phone Number:")
        submit = st.form_submit_button()
    if submit and email and phone_number:
        client = get_sns_client()
        conn = get_connection()
        user = check_if_user_exists(
            conn, {'email': email, 'phone_number': phone_number})
        if user is None:
            st.error(f'''User with email {email} and phone number {
                     phone_number} does not exist''')
        else:
            sms_subscription_arn, email_subscription_arn = get_user_subscription_arn(
                conn, {'email_address': email, 'phone_number': phone_number})
            st.write(sms_subscription_arn)
            st.write(email_subscription_arn)
            unsubscribe_user_from_topic(
                client, email_subscription_arn, sms_subscription_arn)


def create_notifications_page():
    """creates the notification subscription page"""
    st.set_page_config(
        page_title="Earthquake Alerts Subscription",)
    user_info = create_subscription_form()
    create_unsubscribe_form()
    if user_info != []:
        client = get_sns_client()
        conn = get_connection()
        if check_if_user_exists(conn, user_info) is None:
            user_id = upload_user_to_database(conn, user_info)
        if check_if_topic_exists(conn, user_info) is None:
            topic_info = create_topic(client)
            topic_id = upload_topic_to_database(conn, user_info, topic_info)
        email_subscription, sms_subscription = subscribe_to_topic(
            client, topic_info['TopicArn'], user_info)
        upload_user_subscription_to_database(
            conn, user_id, topic_id, email_subscription, sms_subscription)
        conn.commit()


if __name__ == "__main__":
    create_notifications_page()
