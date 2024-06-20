"""This API is to be of use for those who wish to retrieve useful information from our database of earthquake data.
Whether it be an amateur developer or a seasoned researcher, this service should be easy to make the most out of through its endpoints."""
from dotenv import load_dotenv
from flask import Flask, request
import psycopg2
import psycopg2.extras
from psycopg2.extensions import connection, cursor
from os import environ as env

app = Flask(__name__)


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
    return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


def get_earthquake_data() -> list[dict]:
    """return a list of all earthquake data from the database."""
    conn = get_connection()

    search_query = """SELECT * FROM earthquakes
    JOIN magtypes ON magtypes.magtype_id= earthquakes.magtype_id
    JOIN statuses ON statuses.status_id= earthquakes.status_id
    JOIN types ON types.type_id= earthquakes.type_id
    JOIN networks ON networks.network_id= earthquakes.network_id
    JOIN alerts ON alerts.alert_id= earthquakes.alert_id
    """
    with get_cursor(conn) as cur:
        cur.execute(f"{search_query};")
        fetched_earthquakes = cur.fetchall()
    conn.close()
    return fetched_earthquakes


@app.route("/", methods=["GET"])
def endpoint_index():
    return {"message": "Welcome! This is Team Poseidon's API, connected to our Earthquake database. Use this to retrieve information on the earthquake data we have collected."}


@app.route("/earthquakes", methods=["GET"])
def get_earthquakes():
    if request.method == "GET":
        try:
            earthquakes = get_earthquake_data()
            return earthquakes, 200
        except Exception as e:
            return {"error": str(e)}, 400


if __name__ == "__main__":

    load_dotenv()
    app.run(debug=True, host="0.0.0.0", port=5000)
