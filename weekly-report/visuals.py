"A script to create reporting visuals"
from os import environ as ENV
from datetime import datetime, timedelta
import altair as alt
import pandas as pd
import psycopg2
from psycopg2.extensions import connection
from dotenv import load_dotenv
from vega_datasets import data
import geopandas as gpd


WEEK_CONSTRAINT = datetime.now() - timedelta(weeks=1)

WEIGHTING = {
    'avg_magnitude': 0.3,
    'num_earthquakes': 0.2,
    'max_magnitude': 0.4,
    'avg_depth': 0.1
}


def get_connection() -> connection:
    """returns a connection to the earthquake database"""
    load_dotenv()
    return psycopg2.connect(
        user=ENV["DB_USERNAME"],
        password=ENV["DB_PASSWORD"],
        host=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        dbname=ENV["DB_NAME"]
    )


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
                        weekly_data['depth'].min(), weekly_data['depth'].max()],
            range=['green', 'red'])),
        tooltip=['magnitude:Q', 'depth:Q']
    )

    return background + points


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


def get_top_significant_earthquakes(conn: connection) -> list[tuple]:
    """
    Get top 10 significant earthquakes
    A number describing how significant the event is.
    Larger numbers indicate a more significant event.
    This value is determined on a number of factors,
    including: magnitude, maximum MMI, felt reports, and estimated impact.
    """
    with conn.cursor() as cur:
        cur.execute("""
        SELECT title, significance FROM earthquakes
        WHERE time >= %s
        ORDER BY significance DESC
        LIMIT 10; """, (WEEK_CONSTRAINT,))
        result = cur.fetchall()

    return result


def create_significance_bar_chart(data: pd.DataFrame) -> alt.Chart:
    """Create horizontal significant bar chart"""
    data['title'] = data['title'].apply(
        lambda value: value.split(' - ')[1].strip())
    return alt.Chart(data) \
        .mark_bar() \
        .encode(y="title",
                x="significance")


def get_top_magnitude_earthquake(conn: connection) -> list[tuple]:
    """
    Get top recorded earthquake last week
    by magnitude
    """
    with conn.cursor() as cur:
        cur.execute("""
        SELECT title, magnitude FROM earthquakes
        WHERE time >= %s
        ORDER BY magnitude DESC
        LIMIT 1; """, (WEEK_CONSTRAINT,))
        result = cur.fetchone()

    return result


def get_total_number_earthquakes(conn: connection) -> list[tuple]:
    """
    Get total number of recorded earthquakes last week
    """
    with conn.cursor() as cur:
        cur.execute("""
        SELECT COUNT(*) FROM earthquakes
        WHERE time >= %s """, (WEEK_CONSTRAINT,))
        result = cur.fetchone()

    return result[0]


def join_state_locations(usa_earthquakes: pd.DataFrame, state_boundaries) -> gpd.GeoDataFrame:
    """map long and lat coordinates to states in US"""
    usa_earthquakes = gpd.GeoDataFrame(usa_earthquakes, geometry=gpd.points_from_xy(
        usa_earthquakes['longitude'], usa_earthquakes['latitude']))

    usa_earthquakes.crs = state_boundaries.crs

    return gpd.sjoin(usa_earthquakes, state_boundaries[['geometry', 'NAME']],
                     how="left", predicate="within").dropna(subset=['NAME'])


def group_earthquake_by_state(usa_earthquakes: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """groups earthquakes by what state they occur in"""
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
        width=500,
        height=300
    ).project('albersUsa')

    return base + chart


def convert_to_dataframe(data: list[tuple], column_headers: list[str]) -> pd.DataFrame:
    """converts fetched sql data to a dataframe"""
    return pd.DataFrame(data, columns=column_headers)


def get_state_risk_map() -> alt.Chart:
    """gets earthquake data and creates magnitude map visual"""
    conn = get_connection()
    states_gdf = gpd.read_file('/tmp/data/cb_2023_us_state_500k.shp')
    ansi = pd.read_csv(
        'https://www2.census.gov/geo/docs/reference/state.txt', sep='|')
    ansi.columns = ['id', 'abbr', 'state', 'statens']
    usa_earthquakes = get_usa_only_earthquakes(conn)
    usa_earthquakes = convert_to_dataframe(
        usa_earthquakes, ["longitude", "latitude", "magnitude", "depth"])
    usa_earthquakes = join_state_locations(usa_earthquakes, states_gdf)
    usa_earthquakes = group_earthquake_by_state(usa_earthquakes)
    usa_earthquakes = calculate_risk_metric(usa_earthquakes)

    state_background = alt.topo_feature(data.us_10m.url, 'states')
    risk_map = create_risk_state_map(usa_earthquakes, state_background, ansi)
    return risk_map


def get_magnitude_map() -> alt.Chart:
    """gets data and creates magnitude map visual"""
    conn = get_connection()
    earthquakes = get_magnitude_map_data(conn)
    earthquakes = convert_to_dataframe(
        earthquakes, ['lon', 'lat', 'magnitude', 'depth'])
    magnitude_map = create_magnitude_map(earthquakes)

    return magnitude_map


def get_significance_bar() -> alt.Chart:
    """gets data and creates significance chart visual"""
    conn = get_connection()
    earthquakes = get_top_significant_earthquakes(conn)
    earthquakes = convert_to_dataframe(
        earthquakes, ['title', 'significance']
    )
    significance = create_significance_bar_chart(earthquakes)
    return significance


def create_two_layer_pie() -> alt.Chart:
    """creates two-layer-pie chart"""
    conn = get_connection()
    states_gdf = gpd.read_file('/tmp/data/cb_2023_us_state_500k.shp')
    ansi = pd.read_csv(
        'https://www2.census.gov/geo/docs/reference/state.txt', sep='|')
    ansi.columns = ['id', 'abbr', 'state', 'statens']
    usa_earthquakes = get_usa_only_earthquakes(conn)
    usa_earthquakes = convert_to_dataframe(
        usa_earthquakes, ["longitude", "latitude", "magnitude", "depth"])
    usa_earthquakes = join_state_locations(usa_earthquakes, states_gdf)

    bins = [1, 2, 3]
    labels = ['1-2', '2-3']
    usa_earthquakes['magnitude_bin'] = pd.cut(
        usa_earthquakes['magnitude'], bins=bins, labels=labels, right=False)

    usa_earthquakes = usa_earthquakes.groupby(['NAME', 'magnitude_bin']
                                              ).size().reset_index(name='count')
    usa_earthquakes = usa_earthquakes[usa_earthquakes['NAME'].isin(
        ["Alaska", "Hawaii", "Texas", "Nevada"])]

    total_count = usa_earthquakes.groupby('NAME')['count'].sum().reset_index()

    inner = alt.Chart(total_count).mark_arc(innerRadius=0, outerRadius=100).encode(
        theta=alt.Theta(field='count', type='quantitative', stack=True),
        color=alt.Color(field='NAME', type='nominal', legend=None))

    inner_text = alt.Chart(total_count).mark_text(radius=80, size=10).encode(
        theta=alt.Theta(field='count', type='quantitative', stack=True),
        text=alt.Text(field='NAME', type='nominal'),
        color=alt.value('black')
    )

    outer = alt.Chart(usa_earthquakes).mark_arc(innerRadius=100, outerRadius=140).encode(
        theta=alt.Theta(field='count', type='quantitative', stack=True),
        color=alt.Color(field='magnitude_bin', type='nominal'),
        order=alt.Order(field='NAME'),
        detail='NAME'
    )

    outer_text = alt.Chart(usa_earthquakes).mark_text(radius=120, size=12).encode(
        theta=alt.Theta(field='count', type='quantitative', stack=True),
        text=alt.Text(field='magnitude_bin', type='nominal'),
        color=alt.value('black'),
        order=alt.Order(field='NAME'),
        detail='NAME'
    )

    chart = (inner + outer + inner_text + outer_text)
    chart.properties(width=800, height=800)

    return chart


if __name__ == "__main__":
    get_state_risk_map()
    get_magnitude_map()
    get_significance_bar()
    create_two_layer_pie()
