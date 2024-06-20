"A script to connect to the database and create a cursor"
from os import environ as ENV
from dotenv import load_dotenv
import psycopg2
from psycopg2.extensions import connection, cursor
import psycopg2.extras


def get_connection() -> connection:
    """returns a connection to the earthquake database"""
    load_dotenv()
    return psycopg2.connect(
        user=ENV["DB_USERNAME"],
        password=ENV["DB_PASSWORD"],
        host=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        name=ENV["DB_NAME"]
    )


def get_cursor(conn: connection) -> cursor:
    """returns cursor to interact with earthquake database"""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
