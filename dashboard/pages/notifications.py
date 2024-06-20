import streamlit as st
from streamlit_folium import st_folium
import folium
import boto3


DEFAULT_LAT = 51.5072
DEFAULT_LON = 0.1276


def get_sns_client():
    return boto3.client('sns')


def create_topic(client, user_info):
    response = client.create_topic(
        Name='',
        Tags=[{
            'Key': 'latitude',
            'Value': user_info['selected_lat']
        },
            {
            'Key': 'longitude',
            'Value': user_info['selected_lon']
        },
            {
            'Key': 'magnitude',
            'Value': user_info['magnitude']
        }]
    )
    return response


def subscribe_to_topic(topic_ARN, user_info):
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
            ()
        )
        map = st_folium(m)

        if map.get("last_clicked"):
            selected_lat = map["last_clicked"]["lat"]
            selected_lon = map['last_clicked']['lng']

        submit = st.form_submit_button()

    if submit and email and phone_number and selected_lat and selected_lon:
        st.success(f"""Email entered: {email}, Phone Number entered: {
            phone_number}, Position Chosen: {selected_lat}, {selected_lon}""")

        return {'email': email, 'phone_number': phone_number, 'selected_lat': selected_lat, 'selected_lon': selected_lon}

    return []


if __name__ == "__main__":

    user_info = create_subscription_form()
    client = get_sns_client()
