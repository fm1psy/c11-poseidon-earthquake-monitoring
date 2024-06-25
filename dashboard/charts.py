import streamlit as st
import altair as alt
from vega_datasets import data
import pandas as pd


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
