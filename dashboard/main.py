import streamlit as st
from charts import create_magnitude_map
import altair as alt
from vega_datasets import data
from psycopg2.extensions import connection, cursor
import psycopg2.extras
import pandas as pd
from os import environ
from datetime import datetime, timedelta
from dotenv import load_dotenv


WEEK_CONSTRAINT = datetime.now() - timedelta(days=7)
MONTH_CONSTRAINT = datetime.now() - timedelta(days=30)


def get_connection():
    """gets connection to the database"""
    return psycopg2.connect(host=environ['DB_HOST'],
                            dbname=environ['DB_NAME'],
                            user=environ['DB_USERNAME'],
                            password=environ['DB_PASSWORD'],
                            port=environ['DB_PORT'])


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


if __name__ == "__main__":
    st.title("Earthquakes!!!")
    load_dotenv()
    conn = get_connection()

    timeframe = st.radio("Select timeframe:", ["Last 7 days", 'Last 30 days'])
    if timeframe == 'Last 7 days':
        chosen_data = get_magnitude_map_data_last_7_days(conn)
    elif timeframe == 'Last 30 days':
        chosen_data = get_magnitude_map_data_last_30_days(conn)
    st.altair_chart(create_magnitude_map(pd.DataFrame(chosen_data, columns=[
        'lon', 'lat', 'magnitude', 'depth'])))
