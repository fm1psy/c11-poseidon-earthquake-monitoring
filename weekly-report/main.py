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
from visuals import get_significance_bar, get_total_number_earthquakes

CURRENT_DATE = date.today()


def get_s3_client() -> client:
    """Returns input s3 client"""
    try:
        s3_client = client('s3',
                           aws_access_key_id=ENV.get('ACCESS_KEY'),
                           aws_secret_access_key=ENV.get('SECRET_ACCESS_KEY'))
        logging.info(f"""Connected to S3 bucket {
                     ENV.get('STORAGE_BUCKET_NAME')}""")
        return s3_client
    except NoCredentialsError:
        logging.error("Error, no AWS credentials found")
        return None


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


if __name__ == "__main__":
    s_client = get_s3_client()
    count = get_total_number_earthquakes()

    sig_chart = get_significance_bar()
    mag_map = get_magnitude_map()
    state_map = get_state_risk_map()

    sig_html = convert_altair_chart_to_html_embed(sig_chart)
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
            <h2>1. Introduction</h2>
            <p>This report provides an overview of the recent seismic activity globally, with a particular focus on USA. It includes details about the magnitude, location, depth, and potential impact of detected earthquakes. The data is sourced from the United States Geological Survey (USGS).</p>
            <img style="width: 300; height: 100" src="{state_html}">
        </body>
    """
    with open("earthquake_report.html", "w", encoding='utf-8') as f:
        f.write(html_report)

    # file_data = convert_html_to_pdf(html_report)
    # prefix = get_prefix(CURRENT_DATE)
    # file_name = f"{CURRENT_DATE}.pdf"
    # upload_historical_readings(
    #    s_client, ENV['STORAGE_BUCKET_NAME'], prefix, file_name, file_data)
