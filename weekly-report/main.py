"A script to generate weekly PDF reporting"
from datetime import timedelta, date
from os import environ as ENV
import os
from io import BytesIO
import logging
from base64 import b64encode
from xhtml2pdf import pisa
import altair as alt
from boto3 import client
from botocore.exceptions import NoCredentialsError

from visuals import get_state_risk_map, get_magnitude_map
from visuals import get_significance_bar

CURRENT_DATE = date.today()
DESTINATION_DIR = '/tmp/data'


def get_s3_client() -> client:
    """Returns input s3 client"""
    try:
        s3_client = client('s3',
                           aws_access_key_id=ENV.get('ACCESS_KEY'),
                           aws_secret_access_key=ENV.get('SECRET_ACCESS_KEY'))
        return s3_client
    except NoCredentialsError:
        logging.error("Error, no AWS credentials found")
        return None


def get_file_keys_from_bucket(s3, bucket_name: str) -> list[str]:
    """Gets all file Key values from a bucket"""
    bucket = s3.list_objects(Bucket=bucket_name)
    return [file["Key"] for file in bucket["Contents"]]


def download_shapefiles(bucket_name: str, s3: client, folder_path: str) -> None:
    """Downloads shapefiles from bucket"""
    file_keys = get_file_keys_from_bucket(s3, bucket_name)
    for file_key in file_keys:
        file_path = os.path.join(folder_path, file_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        s3.download_file(bucket_name, file_key, file_path)


def convert_altair_chart_to_html_embed(chart: alt.Chart) -> str:
    """Converts an Altair chart to a string representation."""

    with BytesIO() as bs:
        chart.save(bs, format="png")
        bs.seek(0)

        data = b64encode(bs.read()).decode("utf-8")

    return f"data:image/png;base64,{data}"


def convert_html_to_pdf(source_html) -> BytesIO:
    """Outputs HTML to a target file."""
    pdf_output = BytesIO()
    pisa_status = pisa.CreatePDF(
        source_html,
        dest=pdf_output)

    if pisa_status.err:
        raise Exception("error converting html to PDF")
    pdf_output.seek(0)

    return pdf_output


def get_prefix(current_date: date) -> str:
    """creates object prefix for s3 bucket"""
    weekday = current_date.weekday()
    if weekday == 0:
        return f"wc-{current_date.strftime("%d-%m-%Y")}/"

    monday = current_date - timedelta(weekday)
    return f"wc-{monday.strftime("%d-%m-%Y")}/"


def upload_historical_readings(s3: client, bucket_name: str, prefix: str,
                               filename: str, file_data: BytesIO) -> None:
    """uploads the historical readings in memory to the s3 bucket"""
    object_key = os.path.join(prefix, filename)
    s3.upload_fileobj(file_data, bucket_name, object_key)
    logging.info(f"csv file uploaded: {object_key}")


def handler(event=None, context=None):
    """lambda handler function"""
    s_client = get_s3_client()

    download_shapefiles(ENV['SHAPEFILE_BUCKET_NAME'],
                        s_client, DESTINATION_DIR)

    sig_chart = get_significance_bar()
    mag_map = get_magnitude_map()
    state_map = get_state_risk_map()

    mag_html = convert_altair_chart_to_html_embed(mag_map)
    state_html = convert_altair_chart_to_html_embed(state_map)

    html_report = f"""
        <!DOCTYPE html>
        <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <meta charset="utf-8" />
            <title>Weekly Earthquake Monitoring Report</title>
        </head>
        <body>
            <h1>Earthquake Monitoring Report</h1>
            <p><strong>Date:</strong> {CURRENT_DATE}</p>
            <h3>Introduction</h3>
            <p>This report provides an overview of the recent seismic activity globally, with a particular focus on USA. It includes details about the magnitude, location, depth, and potential impact of detected earthquakes. The data is sourced from the United States Geological Survey (USGS).</p>
            <h3>Recent Seismic Activity</h3>
            <p>From June 1, 2024,to June 24, 2024, the seismic monitoring network recorded a total of 15 significant earthquakes. The following visual summarizes the key details of these events.</p>
            <img style="width: 500; height: 300" src="{mag_html}">
            <h3>What's happening in USA?</h3>
            <img style="width: 250; height: 150" src="{state_html}">
        </body>
    """
    file_data = convert_html_to_pdf(html_report)
    prefix = get_prefix(CURRENT_DATE)
    file_name = f"{CURRENT_DATE}.pdf"
    upload_historical_readings(
        s_client, ENV['STORAGE_BUCKET_NAME'], prefix, file_name, file_data)

    return {"success": "complete"}


if __name__ == "__main__":
    handler()
