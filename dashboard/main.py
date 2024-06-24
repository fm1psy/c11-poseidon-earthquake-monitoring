import streamlit as st
from charts import get_world_map_background
import altair as alt


def get_connection():
    ...


def get_last_7_days_data():
    ...


def get_last_30_days_data():
    ...


def get_magnitude_map_data(conn: connection) -> list[tuple]:
    """get this week's earthquake data from db"""
    with conn.cursor() as cur:
        cur.execute("""
        SELECT lon,lat,magnitude,depth FROM earthquakes
        WHERE time >= %s; """, (WEEK_CONSTRAINT,))
        result = cur.fetchall()

    return result


def create_magnitude_map(weekly_data: pd.DataFrame) -> alt.Chart:
    """creates world map chart of current week earthquakes"""
    weekly_data['lon'] = weekly_data['lon'].astype(float)
    weekly_data['lat'] = weekly_data['lat'].astype(float)
    countries = alt.topo_feature(data.world_110m.url, 'countries')
    background = alt.Chart(countries).mark_geoshape(
        fill='lightgray',
        stroke='black',
    ).project(
        "equirectangular"
    ).properties(
        width=1000,
        height=600
    )

    points = alt.Chart(weekly_data).mark_circle().encode(
        longitude='lon',
        latitude='lat',
        size=alt.Size('magnitude:Q', scale=alt.Scale(range=[10, 150])),
        color=alt.Color('depth:Q', scale=alt.Scale(scheme='reds', domain=[
                        weekly_data['depth'].min(), weekly_data['depth'].max()], range=['green', 'red'])),
        tooltip=['magnitude:Q', 'depth:Q']
    )

    return background + points


if __name__ == "__main__":
    st.title("Earthquakes!!!")
