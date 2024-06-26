"""
creates a page in the dashboard that allows users to download the weekly reports stored in an s3 bucket
"""
import base64
import logging
from os import environ
from datetime import timedelta, date
import os
import streamlit as st
from boto3 import client
from botocore.exceptions import NoCredentialsError

CURRENT_DATE = date.today()
BUCKET_NAME = environ["BUCKET_NAME"]


def get_s3_client() -> client:
    """Returns input s3 client"""
    try:
        s3_client = client('s3',
                           aws_access_key_id=environ.get('ACCESS_KEY'),
                           aws_secret_access_key=environ.get('SECRET_ACCESS_KEY'))
        return s3_client
    except NoCredentialsError:
        logging.error("Error, no AWS credentials found")
        return None


def get_prefix(current_date: date) -> str:
    """creates object prefix for s3 bucket"""
    weekday = current_date.weekday()
    if weekday == 0:
        return f"wc-{current_date.strftime("%d-%m-%Y")}/"

    monday = current_date - timedelta(weekday)
    return f"wc-{monday.strftime("%d-%m-%Y")}/"


def get_s3_file(s3_client, bucket_name, file_key):
    """
    Fetches a file from S3 and returns it as a bytes object.
    """
    try:
        obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        return obj['Body'].read()
    except NoCredentialsError:
        st.error("AWS S3 credentials are not configured properly.")
        return None
    except Exception as e:
        st.error(f"Failed to fetch file from S3: {e}")
        return None


def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object stored in memory.
    """
    if object_to_download is not None:
        # Create a download button for the object
        b64 = base64.b64encode(object_to_download).decode()
        href = f'<a href="data:file/html;base64,{b64}" download="{
            download_filename}">{download_link_text}</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.error("No file to download.")


def list_s3_objects(s3_client, bucket):
    """returns a list of all s3 objects in the given bucket"""
    return s3_client.list_objects(Bucket=bucket)


def create_page():
    """creates the weekly report page"""
    st.title("Weekly Report")
    st.subheader(
        "A pdf report is produced every week with information on that weeks earthquakes.")
    st.subheader("To download the most recent report, click below:")

    s3_client = get_s3_client()
    folder = get_prefix(CURRENT_DATE)
    test_file_name = "2024-06-26.pdf"
    object_key = os.path.join(folder, test_file_name)
    # Use Streamlit's download button to enable file download
    st.download_button(label=f"Download report: {test_file_name}",
                       data=get_s3_file(
                           s3_client, BUCKET_NAME, object_key),
                       file_name=test_file_name,
                       )
    st.write("Previous weekly reports are also available below:")
    for s3_object in list_s3_objects(s3_client, bucket=BUCKET_NAME)["Contents"]:
        st.download_button(label=f"Download report: {s3_object["Key"]}",
                           data=get_s3_file(
                           s3_client, BUCKET_NAME, s3_object["Key"]),
                           file_name=s3_object["Key"],
                           )


if __name__ == "__main__":
    create_page()
