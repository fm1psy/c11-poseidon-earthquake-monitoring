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
import geopandas as gpd


WEEK_CONSTRAINT = datetime.now() - timedelta(days=7)
MONTH_CONSTRAINT = datetime.now() - timedelta(days=30)
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
            WHERE time >= %s AND
            (
                (lat BETWEEN %s AND %s AND lon BETWEEN %s AND %s) OR
                (lat BETWEEN %s AND %s AND lon BETWEEN %s AND %s) OR
                (lat BETWEEN %s AND %s AND lon BETWEEN %s AND %s)
                    ) """,
                    (WEEK_CONSTRAINT, cont_us_lat[0], cont_us_lat[1],
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
    state_grouping['risk_score'] = (
        state_grouping['num_earthquakes'] * WEIGHTING.get('num_earthquakes') +
        state_grouping['avg_magnitude'] * WEIGHTING.get('avg_magnitude') +
        state_grouping['max_magnitude'] * WEIGHTING.get('max_magnitude') +
        state_grouping['num_earthquakes'] * WEIGHTING.get('num_earthquakes') +
        state_grouping['avg_depth'] * WEIGHTING.get('avg_depth'))

    return state_grouping


def create_risk_state_map(state_grouping: gpd.GeoDataFrame,
                          us_state_map: alt.topo_feature, ansi: pd.DataFrame) -> alt.Chart:
    """creates colour-coded us state map dictated by risk score"""
    state_grouping = pd.merge(
        state_grouping, ansi[['state', 'id']], how='left', left_on='NAME', right_on='state')

    base = alt.Chart(us_state_map).mark_geoshape(
        fill='lightgray', stroke='black', strokeWidth=0.5)

    chart = alt.Chart(us_state_map).mark_geoshape(stroke='black').encode(
        color=alt.Color(
            'risk_score:Q',
            scale=alt.Scale(
                domain=[state_grouping['risk_score'].min(
                ), state_grouping['risk_score'].max()],
                range=['#FDFD96', '#FF0000']
            ),
            legend=alt.Legend(title="Risk Score")),
        tooltip=['risk_score:Q']
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(state_grouping, 'id', ['risk_score'])
    ).properties(
        width=1000,
        height=600
    ).project('albersUsa')

    return base + chart


def convert_to_dataframe(data: list[tuple], column_headers: list[str]) -> pd.DataFrame:
    """converts fetched sql data to a dataframe"""
    return pd.DataFrame(data, columns=column_headers)


def get_state_risk_map() -> alt.Chart:
    """gets earthquake data and creates magnitude map visual"""
    conn = get_connection()
    states_gdf = gpd.read_file(
        './cb_2023_us_state_500k/cb_2023_us_state_500k.shp')
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


if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.title("Earthquake Dashboard")

    load_dotenv()
    conn = get_connection()
    recent_earthquake_loc, recent_earthquake_time, recent_earthquake_mag = get_most_recent_earthquake_above_mag_5(
        conn)
    st.subheader(
        f"The most recent significant earthquake was recorded in {recent_earthquake_loc} at {recent_earthquake_time} with a magnitude of {recent_earthquake_mag}.")

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

    st.subheader(
        "The map below shows the states of the US colour coded by the risk posed by earthquakes:")
    st.altair_chart(get_state_risk_map())
