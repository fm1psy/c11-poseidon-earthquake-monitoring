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
from dotenv import load_dotenv

from visuals import get_state_risk_map, get_magnitude_map, get_total_number_earthquakes, create_two_layer_pie
from visuals import get_significance_bar, get_top_magnitude_earthquake, get_top_significant_earthquakes, get_connection

load_dotenv()

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
    """Downloads shapefiles for US state mapping"""
    file_keys = get_file_keys_from_bucket(s3, bucket_name)
    for file_key in file_keys:
        file_path = os.path.join(folder_path, file_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        s3.download_file(bucket_name, file_key, file_path)


def monday_week_date(current_date: date) -> str:
    weekday = current_date.weekday()
    if weekday == 0:
        return current_date.strftime("%d-%m-%Y")

    monday = current_date - timedelta(weekday)
    return monday.strftime("%d-%m-%Y")


def previous_monday(current_date: date) -> date:
    """Returns the previous Monday from the given date."""
    weekday = current_date.weekday()
    previous_monday = current_date - \
        timedelta(days=weekday + 7 if weekday == 0 else weekday)
    return previous_monday


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
    return f"wc-{monday_week_date(current_date)}/"


def upload_historical_readings(s3: client, bucket_name: str, prefix: str,
                               filename: str, file_data: BytesIO) -> None:
    """uploads the historical readings in memory to the s3 bucket"""
    object_key = os.path.join(prefix, filename)
    s3.upload_fileobj(file_data, bucket_name, object_key)
    logging.info(f"csv file uploaded: {object_key}")


def convert_altair_chart_to_html_embed(chart: alt.Chart) -> str:
    """Converts an Altair chart to a base64-encoded PNG string."""
    chart_png = chart.to_dict()
    chart_png = alt.Chart.from_dict(chart_png).to_json()

    png_output = BytesIO()
    with alt.renderers.enable('png'):
        chart.save(png_output, format='png')
    png_output.seek(0)
    data = b64encode(png_output.read()).decode("utf-8")
    return f"data:image/png;base64,{data}"


def handler(event=None, context=None):
    """lambda handler function"""
    s_client = get_s3_client()
    con = get_connection()

    download_shapefiles(ENV['SHAPEFILE_BUCKET_NAME'],
                        s_client, DESTINATION_DIR)
    logging.info(f"Shapefiles downloaded from {ENV['SHAPEFILE_BUCKET_NAME']}")

    sig_chart = get_significance_bar()
    mag_map = get_magnitude_map()
    state_map = get_state_risk_map()
    two_layer_pie = create_two_layer_pie()

    mag_html = convert_altair_chart_to_html_embed(mag_map)
    state_html = convert_altair_chart_to_html_embed(state_map)
    pie_html = convert_altair_chart_to_html_embed(two_layer_pie)

    total_earthquakes = get_total_number_earthquakes(con)
    highest_magnitude = get_top_magnitude_earthquake(con)[1]
    most_significant_earthquake = get_top_significant_earthquakes(con)[0][1]
    logging.info("Altair charts converted to html")

    prev_monday = previous_monday(CURRENT_DATE).strftime("%B %d, %Y")

    html_report = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>Weekly Earthquake Monitoring Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            table {{
                width: 100%;
                border-collapse: collapse;
            }}
            .date {{
                padding-left: 100%;
            }}
            .data-table, .data-table th, .data-table td {{
                border: 1px solid black;
            }}
            .data-table th, .data-table td {{
                padding: 10px;
                text-align: center;
            }}
            .value-holder {{
                font-size: 14px;
                font-weight: bold;
            }}
            .image-container {{
                text-align: center;
                margin: 20px 0;
            }}
            .image-container img {{
                display: block;
                margin: 0 auto;
            }}
        </style>
    </head>
    <body>
        <table>
            <tr>
                <td style="vertical-align: top;">
                    <h1>Earthquake Monitoring Report</h1>
                </td>
                <td style="padding-left: 20px;">
                    <p class="date"><strong>Date:</strong> {CURRENT_DATE}</p>
                </td>
            </tr>
        </table>
        <h3>Introduction</h3>
        <p>This report provides an overview of the recent seismic activity globally, with a particular focus on the USA. It includes details about the magnitude, location, depth, and potential impact of detected earthquakes. The data is sourced from the United States Geological Survey (USGS).</p>
        <table class="data-table">
            <tr>
                <th>Total No. of Earthquakes</th>
                <th>Highest Recorded Magnitude</th>
                <th>Most Significant Earthquake</th>
            </tr>
            <tr>
                <td class="value-holder">{total_earthquakes}</td>
                <td class="value-holder">{highest_magnitude}</td>
                <td class="value-holder">{most_significant_earthquake}</td>
            </tr>
        </table>
        <h3>Recent Seismic Activity</h3>
        <p>From {prev_monday} to {CURRENT_DATE.strftime("%B %d, %Y")}, the seismic monitoring network recorded a total of {total_earthquakes} earthquakes. The following visual summarizes the key details of these events.</p>
        <div class="image-container" style="margin-bottom: 30px">
            <img style="width: 500px; height: 300px;" src="{mag_html}" alt="Magnitude Map">
        </div>
        <table style="margin-bottom: 20px;">
            <tr>
                <td style="vertical-align: top;">
                    <img src="{state_html}" alt="State Risk Map" style="height:200px; width: 400px;">
                </td>
                <td style="padding-left: 20px;">
                    <p>Text description or analysis related to the state risk map goes here.</p>
                </td>
            </tr>
        </table>
        <table>
            <tr>
                <td style="vertical-align: top; padding-left: 40px;">
                    <img src="{pie_html}" alt="Pie" style="height:200px; width: 200px;">
                </td>
                <td style="padding-left: 20px;">
                    <p>Text description or analysis related to the two layer pie chart goes here.</p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    file_data = convert_html_to_pdf(html_report)
    logging.info("Weekly report converted from HTML to PDF")
    prefix = get_prefix(CURRENT_DATE)
    file_name = f"{CURRENT_DATE}.pdf"
    upload_historical_readings(
        s_client, ENV['STORAGE_BUCKET_NAME'], prefix, file_name, file_data)
    logging.info(f"Weekly PDF report uploaded to {ENV['STORAGE_BUCKET_NAME']}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    handler()
