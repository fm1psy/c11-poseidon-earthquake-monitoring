import streamlit as st
from charts import create_magnitude_map, create_risk_state_map
import altair as alt
from vega_datasets import data
from psycopg2.extensions import connection, cursor
import psycopg2.extras
import pandas as pd
import os
from os import environ
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import geopandas as gpd
from st_pages import Page, show_pages, add_page_title
from boto3 import client
from botocore.exceptions import NoCredentialsError


WEEK_CONSTRAINT = datetime.now() - timedelta(days=7)
MONTH_CONSTRAINT = datetime.now() - timedelta(days=30)
DESTINATION_DIR = '/tmp/data'
WEIGHTING = {
    'avg_magnitude': 0.3,
    'num_earthquakes': 0.2,
    'max_magnitude': 0.4,
    'avg_depth': 0.1
}


def get_connection():
    """gets connection to the database"""
    return psycopg2.connect(host=environ['DB_HOST'],
                            dbname=environ['DB_NAME'],
                            user=environ['DB_USERNAME'],
                            password=environ['DB_PASSWORD'],
                            port=environ['DB_PORT'])


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


def get_magnitude_map_data_last_7_days(conn: connection) -> list[tuple]:
    """get last 7 days earthquake data from db"""
    with conn.cursor() as cur:
        cur.execute("""
        SELECT lon,lat,magnitude,depth FROM earthquakes
        WHERE time >= %s; """, (WEEK_CONSTRAINT,))
        result = cur.fetchall()

    return result


def get_magnitude_map_data_last_30_days(conn: connection) -> list[tuple]:
    """get last 30 days earthquake data from db"""
    with conn.cursor() as cur:
        cur.execute("""
        SELECT lon,lat,magnitude,depth FROM earthquakes
        WHERE time >= %s; """, (MONTH_CONSTRAINT,))
        result = cur.fetchall()

    return result


def get_usa_only_earthquakes(conn: connection) -> list[tuple]:
    """ Get all earthquakes within the us"""
    cont_us_lat = [24.396308, 49.384358]
    cont_us_lon = [-125.000000, -66.934570]
    hawaii_lat = [18.910361, 28.402123]
    hawaii_lon = [-178.334698, -154.806773]
    alaska_lat = [51.209712, 71.538800]
    alaska_lon = [-179.148909, -129.979506]

    with conn.cursor() as cur:
        cur.execute("""
        SELECT lon,lat,magnitude, depth FROM earthquakes
            WHERE
            (
                (lat BETWEEN %s AND %s AND lon BETWEEN %s AND %s) OR
                (lat BETWEEN %s AND %s AND lon BETWEEN %s AND %s) OR
                (lat BETWEEN %s AND %s AND lon BETWEEN %s AND %s)
                    ) """,
                    (cont_us_lat[0], cont_us_lat[1],
                     cont_us_lon[0], cont_us_lon[1],
                     hawaii_lat[0], hawaii_lat[1],
                     hawaii_lon[0], hawaii_lon[1],
                     alaska_lat[0], alaska_lat[1],
                     alaska_lon[0], alaska_lon[1]))

        result = cur.fetchall()
    return result


def group_earthquake_by_state(usa_earthquakes: pd.DataFrame,
                              state_boundaries: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """groups earthquakes by what state they occur in"""
    usa_earthquakes = gpd.GeoDataFrame(usa_earthquakes, geometry=gpd.points_from_xy(
        usa_earthquakes['longitude'], usa_earthquakes['latitude']))

    usa_earthquakes.crs = state_boundaries.crs

    usa_earthquakes = gpd.sjoin(usa_earthquakes, state_boundaries[['geometry', 'NAME']],
                                how="left", predicate="within").dropna(subset=['NAME'])

    return usa_earthquakes.groupby('NAME').agg(num_earthquakes=('magnitude', 'size'),
                                               avg_magnitude=(
                                                   'magnitude', 'mean'),
                                               max_magnitude=(
                                                   'magnitude', 'max'),
                                               avg_depth=('depth', 'mean')).reset_index()


def calculate_risk_metric(state_grouping: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    calculates risk associated with living in a us state
    susceptible to earthquakes
    """
    state_grouping['relative_risk'] = (
        state_grouping['num_earthquakes'] * WEIGHTING.get('num_earthquakes') +
        state_grouping['avg_magnitude'] * WEIGHTING.get('avg_magnitude') +
        state_grouping['max_magnitude'] * WEIGHTING.get('max_magnitude') +
        state_grouping['num_earthquakes'] * WEIGHTING.get('num_earthquakes') +
        state_grouping['avg_depth'] * WEIGHTING.get('avg_depth'))

    return state_grouping


def convert_to_dataframe(data: list[tuple], column_headers: list[str]) -> pd.DataFrame:
    """converts fetched sql data to a dataframe"""
    return pd.DataFrame(data, columns=column_headers)


def get_most_recent_earthquake_above_mag_5(conn):
    with conn.cursor() as cur:
        cur.execute(
            """select title, time, magnitude from earthquakes where magnitude >= 5 order by time DESC limit 1; """)
        result = cur.fetchone()
    return result


def get_avg_magnitude_last_7_days(conn):
    with conn.cursor() as cur:
        cur.execute("""
        SELECT AVG(magnitude) depth FROM earthquakes
        WHERE time >= %s; """, (WEEK_CONSTRAINT,))
        result = cur.fetchone()
    return result


def get_avg_magnitude_last_30_days(conn):
    with conn.cursor() as cur:
        cur.execute("""
        SELECT AVG(magnitude) depth FROM earthquakes
        WHERE time >= %s; """, (MONTH_CONSTRAINT,))
        result = cur.fetchone()
    return result


def get_file_keys_from_bucket(s3, bucket_name: str) -> list[str]:
    """Gets all file Key values from a bucket"""
    bucket = s3.list_objects(Bucket=bucket_name)
    return [file["Key"] for file in bucket["Contents"]]


@st.cache_data
def download_shapefiles(_bucket_name: str, _s3: client, _folder_path: str) -> None:
    """Downloads shapefiles for US state mapping"""
    file_keys = get_file_keys_from_bucket(_s3, _bucket_name)
    for file_key in file_keys:
        file_path = os.path.join(_folder_path, file_key)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        _s3.download_file(_bucket_name, file_key, file_path)


def get_state_risk_map() -> alt.Chart:
    """gets earthquake data and creates magnitude map visual"""
    conn = get_connection()
    states_gdf = gpd.read_file(
        '/tmp/data/cb_2023_us_state_500k.shp')
    ansi = pd.read_csv(
        'https://www2.census.gov/geo/docs/reference/state.txt', sep='|')
    ansi.columns = ['id', 'abbr', 'state', 'statens']
    usa_earthquakes = get_usa_only_earthquakes(conn)
    usa_earthquakes = convert_to_dataframe(
        usa_earthquakes, ["longitude", "latitude", "magnitude", "depth"])
    usa_earthquakes = group_earthquake_by_state(usa_earthquakes, states_gdf)
    usa_earthquakes = calculate_risk_metric(usa_earthquakes)

    state_background = alt.topo_feature(data.us_10m.url, 'states')
    risk_map = create_risk_state_map(usa_earthquakes, state_background, ansi)
    return risk_map


def create_magnitude_table():
    data = {'Magnitude': ['0 - 2.9', '3.0 - 3.9', '4.0 - 4.9', '5.0 - 5.9',
                          '6.0 - 6.9', '7.0 - 7.9', '8.0 +'], 'Category': ['micro', 'minor', 'light', 'moderate', 'strong', 'major', 'great'], 'Impact': ['Recorded on instruments but so small that they are not usually felt by people', 'Felt by some people but minimal damage caused', 'Small amounts of damage caused, felt by majority of people in the area', 'Weaker structures face some damage', 'Moderate damage to structures', 'Serious damage to large areas and potential loss of life', 'Severe and serious damage and significant loss of life'], 'Average number occuring per year': ['Over 100,000', '12,000 - 100,000', '2,000 - 12,000', '200 - 2,000', '20 - 200', '3 - 200', 'fewer than 3']}
    return st.table(pd.DataFrame.from_dict(data, orient='columns'))


def create_risk_table():
    data = {'Parameter': ['Number of Earthquakes',
                          'Average Magnitude', 'Maximum Magnitude', 'Average Depth'], 'Risk Weighting': ['0.2', '0.3', '0.4', '0.1']}
    return st.table(pd.DataFrame.from_dict(data, orient='columns'))


def create_home_page():
    """creates the home page"""
    st.set_page_config(layout="wide")
    show_pages(
        [
            Page("main.py", "Home", "🏠"),
            Page("pages/notifications.py",
                 "Earthquake Notifications", ":rotating_light:"),
            Page("pages/weekly_report.py",
                 "Weekly PDF Report", ":page_facing_up:")
        ]
    )
    st.title("Earthquake Dashboard :earth_americas:")

    load_dotenv()
    conn = get_connection()
    recent_earthquake_loc, recent_earthquake_time, recent_earthquake_mag = get_most_recent_earthquake_above_mag_5(
        conn)
    st.subheader(
        f"The most recent significant earthquake was recorded in {recent_earthquake_loc.split("-")[1]} at {recent_earthquake_time} with a magnitude of {recent_earthquake_mag}.")

    with st.expander('Click here for more information on earthquake magnitudes'):
        st.write(
            "Earthquake magnitude is essentially the size of the earthquake measured, the table below provides more information on how the impact of earthquakes changes as the magnitude increases:")
        create_magnitude_table()

    timeframe = st.radio("Select timeframe:", [
        "Last 7 days", 'Last 30 days'])
    if timeframe == 'Last 7 days':
        chosen_data = get_magnitude_map_data_last_7_days(conn)
        avg_magnitude = get_avg_magnitude_last_7_days(conn)
    elif timeframe == 'Last 30 days':
        chosen_data = get_magnitude_map_data_last_30_days(conn)
        avg_magnitude = get_avg_magnitude_last_30_days(conn)
    st.write(f"""The average magnitude of all earthquakes in the {
        timeframe} is {avg_magnitude}""")
    st.altair_chart(create_magnitude_map(pd.DataFrame(chosen_data, columns=[
        'lon', 'lat', 'magnitude', 'depth'])))

    s_client = get_s3_client()

    download_shapefiles(environ['SHAPEFILE_BUCKET_NAME'],
                        s_client, DESTINATION_DIR)

    st.subheader(
        "The map below shows the states of the US colour coded by the relative risk posed by earthquakes:")
    st.altair_chart(get_state_risk_map())

    with st.expander("Click here for more information about how earthquake risk is calculated:"):
        st.write("To determine the relative risk associated with living in a US state susceptible to earthquakes a risk metric was calculated as function of 4 different parameters, with each parameter assigned a risk weighting score dictating the their contribution to the final overall score.")
        create_risk_table()


if __name__ == "__main__":
    create_home_page()
