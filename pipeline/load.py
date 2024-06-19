"""This file is responsible for loading data into the RDS"""

import os

from psycopg2.extensions import connection, cursor
from dotenv import load_dotenv
import psycopg2.extras

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')


def get_connection(host: str, name: str, user: str, password: str, port: str) -> connection:
    '''Creates a psycopg2 connection'''
    conn = psycopg2.connect(host=host, dbname=name,
                            user=user, password=password, port=port)
    return conn


def get_cursor(conn: connection) -> cursor:
    '''Creates a cursor based on provided psycopg2 connection'''
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return cursor


def get_all_networks(cursor: cursor) -> list:
    """Gets all networks in RDS"""
    formatted_networks = {}
    cursor.execute("""SELECT * FROM networks;""")
    networks = cursor.fetchall()
    for network in networks:
        formatted_networks[network["network_name"]] = network["network_id"]
    return formatted_networks


def get_all_statuses(cursor: cursor) -> list:
    """Gets all statuses in RDS"""
    formatted_statuses = {}
    cursor.execute("""SELECT * FROM statuses;""")
    statuses = cursor.fetchall()
    for status in statuses:
        formatted_statuses[status["status_value"]] = status["status_id"]
    return formatted_statuses


def get_all_magtypes(cursor: cursor) -> list:
    """Gets all magTypes in RDS"""
    formatted_magtypes = {}
    cursor.execute("""SELECT * FROM magtypes;""")
    magtypes = cursor.fetchall()
    for magtype in magtypes:
        formatted_magtypes[magtype["magtype_value"]] = magtype["magtype_id"]
    return formatted_magtypes


def get_all_types(cursor: cursor) -> list:
    """Gets all types in RDS"""
    formatted_types = {}
    cursor.execute("""SELECT * FROM types;""")
    types = cursor.fetchall()
    for type in types:
        formatted_types[type["type_value"]] = type["type_id"]
    return formatted_types


if __name__ == "__main__":
    con = get_connection(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, DB_PORT)
    cur = get_cursor(con)
