import streamlit as st
from streamlit_folium import st_folium
import folium
import boto3
from os import environ
from dotenv import load_dotenv


DEFAULT_LAT = 51.5072
DEFAULT_LON = 0.1276


def get_sns_client():
    load_dotenv()
    return boto3.client(
        'sns',
        aws_access_key_id=environ['ACCESS_KEY'],
        aws_secret_access_key=environ['SECRET_ACCESS_KEY'])


def create_topic(client, user_info):
    response = client.create_topic(
        Name='c11-ella-test2',
        Tags=[{
            'Key': 'latitude',
            'Value': str(user_info['selected_lat'])
        },
            {
            'Key': 'longitude',
            'Value': str(user_info['selected_lon'])
        },
            {
            'Key': 'magnitude',
            'Value': user_info['magnitude']
        }]
    )
    return response


def subscribe_to_topic(topic_ARN, user_info):
    email_response = client.subscribe(
        TopicArn=topic_ARN['TopicArn'],
        Protocol='email',
        Endpoint=user_info['email']
    )
    sms_response = client.subscribe(
        TopicArn=topic_ARN['TopicArn'],
        Protocol='sms',
        Endpoint=user_info['phone_number']
    )
    return email_response


def check_if_topic_exists(client, user_info):
    topics = client.list_topics()['Topics']

    for topic in topics:
        latitude = False
        longitude = False
        magnitude = False
        tags = client.list_tags_for_resource(
            ResourceArn=topic['TopicArn'])['Tags']
        for tag in tags:
            if tag['Key'] == 'latitude' and tag['Value'] == str(user_info['selected_lat']):
                latitude = True
            elif tag['Key'] == 'longitude' and tag['Value'] == str(user_info['selected_lon']):
                longitude = True
            elif tag['Key'] == 'magnitude' and tag['Value'] == user_info['magnitude']:
                magnitude = True
        if latitude and longitude and magnitude:
            return topic['TopicArn']
    return None


def unsubscribe_to_topic():
    ...


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

        return {'email': email, 'phone_number': phone_number, 'selected_lat': selected_lat, 'selected_lon': selected_lon, 'magnitude': magnitude}

    return []


if __name__ == "__main__":

    user_info = create_subscription_form()
    if user_info:
        client = get_sns_client()
        if check_if_topic_exists(client, user_info) is None:
            st.write('topic does not exist')
            topic_arn = create_topic(client, user_info)
            st.write(topic_arn)
        else:
            st.write('topic already exists')
        email_response = subscribe_to_topic(topic_arn, user_info)

        st.write(email_response)
