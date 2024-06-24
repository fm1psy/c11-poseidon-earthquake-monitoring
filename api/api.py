"""This API is to be of use for those who wish to retrieve useful information from our database of
earthquake data. Whether it be an amateur developer or a seasoned researcher, this service should
be easy to make the most out of through its endpoints."""
from os import environ as env
from dotenv import load_dotenv
from flask import Flask, Response, request
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection, cursor

app = Flask(__name__)

STATUS_FILTER_KEY = "status_filter"
NETWORK_FILTER_KEY = "network_filter"
ALERT_FILTER_KEY = "alert_filter"
MAG_TYPE_FILTER_KEY = "mag_type_filter"
EVENT_FILTER_KEY = "event_filter"
MIN_MAGNITUDE_FILTER_KEY = "min_magnitude_filter"
CONTINENT_FILTER_KEY = "continent_filter"


def get_connection() -> connection:
    """Return a connection object associated with the earthquake database"""
    return psycopg2.connect(
        user=env["DB_USERNAME"],
        password=env["DB_PASSWORD"],
        host=env["DB_HOST"],
        port=env["DB_PORT"],
        database=env["DB_NAME"]
    )


def get_cursor(conn: connection) -> cursor:
    """Return a cursor object based on the connection passed."""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def get_filter_queries(earthquake_filters: dict[str]) -> list[str]:
    """Return a list of WHERE command strings that can be added onto a postgreSQL query.
    """
    res = []
    status = earthquake_filters[STATUS_FILTER_KEY]
    network = earthquake_filters[NETWORK_FILTER_KEY]
    alert = earthquake_filters[ALERT_FILTER_KEY]
    magtype = earthquake_filters[MAG_TYPE_FILTER_KEY]
    event = earthquake_filters[EVENT_FILTER_KEY]
    min_magnitude = earthquake_filters[MIN_MAGNITUDE_FILTER_KEY]
    continent = earthquake_filters[CONTINENT_FILTER_KEY]
    if status is not None:
        res.append(f"s.status = '{status}'")
    if network is not None:
        res.append(f"n.network_name = '{network}'")
    if alert is not None:
        res.append(f"a.alert_value = '{alert}'")
    if magtype is not None:
        res.append(f"mt.magtype_value = '{magtype}'")
    if event is not None:
        res.append(f"t.type_value = '{event}'")
    if min_magnitude is not None:
        res.append(f"e.magnitude >= '{min_magnitude}'")
    if continent is not None:
        # TODO: implement api to get continent filter working
        res.append("NOT YET IMPLEMENTED")
    res[0] = "WHERE "+res[0]
    return res


def get_all_earthquakes(earthquake_filters: dict[str]) -> list[dict]:
    """Return a list of all earthquake data from the database."""
    conn = get_connection()

    search_query = """SELECT e.earthquake_id,e.magnitude,e.lon,e.lat,e.time,e.felt,e.cdi,e.mmi,
    e.significance,e.nst,e.dmin,e.gap,e.title,e.depth,
    mt.magtype_value as magtype, s.status, t.type_value as cause_of_event, n.network_name, a.alert_value as alert FROM earthquakes AS e
    LEFT JOIN magtypes AS mt USING(magtype_id)
    LEFT JOIN statuses AS s USING(status_id)
    LEFT JOIN types AS t USING(type_id)
    LEFT JOIN networks AS n USING(network_id)
    LEFT JOIN alerts AS a USING(alert_id)
    """
    if any(value is not None for value in earthquake_filters.values()):
        query_filter_commands = get_filter_queries(earthquake_filters)
        search_query += " AND ".join(query_filter_commands)

    with get_cursor(conn) as cur:
        cur.execute(search_query)
        fetched_earthquakes = cur.fetchall()
    conn.close()
    return fetched_earthquakes


@app.route("/", methods=["GET"])
def endpoint_index() -> Response:
    """This is the default endpoint, displaying a basic message"""
    return {"message": "Welcome! This is Team Poseidon's Earthquake Monitoring API!"}, 200


@app.route("/earthquakes", methods=["GET"])
def get_earthquakes() -> Response:
    """This endpoint returns a list containing data on every earthquake in our system."""
    try:
        user_filters = {
            STATUS_FILTER_KEY: request.args.get("status"),
            NETWORK_FILTER_KEY: request.args.get("network"),
            ALERT_FILTER_KEY: request.args.get("alert"),
            MAG_TYPE_FILTER_KEY: request.args.get("mag_type"),
            EVENT_FILTER_KEY: request.args.get("event"),
            MIN_MAGNITUDE_FILTER_KEY: request.args.get("min_magnitude"),
            CONTINENT_FILTER_KEY: request.args.get("continent")
        }

        earthquakes = get_all_earthquakes(user_filters)
        return earthquakes, 200
    except Exception as e:  # pylint: disable=broad-exception-caught
        return {"error": str(e)}, 400


if __name__ == "__main__":
    load_dotenv()
    app.run(debug=True, host="0.0.0.0", port=5000)
