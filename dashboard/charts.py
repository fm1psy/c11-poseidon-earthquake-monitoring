import streamlit as st
import altair as alt
from vega_datasets import data
import pandas as pd
import geopandas as gpd


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


def create_risk_state_map(state_grouping: gpd.GeoDataFrame,
                          us_state_map: alt.topo_feature, ansi: pd.DataFrame) -> alt.Chart:
    """creates colour-coded us state map dictated by risk score"""
    state_grouping = pd.merge(
        state_grouping, ansi[['state', 'id']], how='left', left_on='NAME', right_on='state')

    base = alt.Chart(us_state_map).mark_geoshape(
        fill='lightgray', stroke='black', strokeWidth=0.5)

    chart = alt.Chart(us_state_map).mark_geoshape(stroke='black').encode(
        color=alt.Color(
            'relative_risk:Q',
            scale=alt.Scale(
                domain=[state_grouping['relative_risk'].min(
                ), state_grouping['relative_risk'].max()],
                range=['#FDFD96', '#FF0000']
            ),
            legend=alt.Legend(title="Relative Risk",
                              labelExpr='')),
        tooltip=['relative_risk:Q']
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(state_grouping, 'id', ['relative_risk'])
    ).properties(
        width=1000,
        height=600
    ).project('albersUsa')

    return base + chart
