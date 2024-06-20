"""This file is responsible for loading data into the RDS"""
# pylint: disable=W0718, W0621

import os
import logging

from psycopg2.extensions import connection, cursor
from psycopg2 import OperationalError
from dotenv import load_dotenv
import psycopg2.extras

from extract import extract_process
from transform import transform_process

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')
ALERT = "alert"
STATUS = "status"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")


def get_connection(host: str, name: str, user: str, password: str, port: str) -> connection:
    '''Creates a psycopg2 connection'''
    try:
        conn = psycopg2.connect(host=host, dbname=name,
                                user=user, password=password, port=port)
        logging.info("Connection established successfully")
        return conn
    except OperationalError as e:
        logging.error(
            f"OperationalError occurred while trying to connect to the database: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None


def get_cursor(conn: connection) -> cursor:
    '''Creates a cursor based on provided psycopg2 connection'''
    logging.info("Creating a cursor from the psycopg2 connection")
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        logging.info("Cursor created successfully")
        return cursor
    except OperationalError as e:
        logging.error(
            f"OperationalError occurred while trying to create a cursor: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return None


def execute_query(cursor: cursor, query: str) -> list:
    """Executes a query and returns the results."""
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except OperationalError as e:
        logging.error(f"OperationalError occurred while executing query: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    return None


def execute_insert(conn: connection, cursor: cursor, query: str, args: tuple) -> int:
    """Executes an insert query and returns the new ID"""
    try:
        cursor.execute(query, args)
        new_id = cursor.fetchone()[0]
        conn.commit()
        return new_id
    except (psycopg2.IntegrityError, psycopg2.OperationalError, psycopg2.DatabaseError) as e:
        logging.error(f"Database error: {e}")
        conn.rollback()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        conn.rollback()
    return None


def fetch_all(cursor: cursor, table: str, key_field: str, value_field: str) -> dict:
    """Gets all records from a given table and returns a dictionary"""
    logging.info(f"Fetching all values from {table}")
    query = f"SELECT * FROM {table};"
    results = execute_query(cursor, query)
    return {record[key_field]: record[value_field] for record in results} if results else {}


def get_all_alerts(cursor: cursor) -> dict:
    "Fetches all alert values from RDS"
    return fetch_all(cursor, "alerts", "alert_value", "alert_id")


def get_all_networks(cursor: cursor) -> dict:
    "Fetches all network values from RDS"
    return fetch_all(cursor, "networks", "network_name", "network_id")


def get_all_statuses(cursor: cursor) -> dict:
    "Fetches all statuses from RDS"
    return fetch_all(cursor, "statuses", STATUS, "status_id")


def get_all_magtypes(cursor: cursor) -> dict:
    "Fetches all magtypes values from RDS"
    return fetch_all(cursor, "magtypes", "magtype_value", "magtype_id")


def get_all_types(cursor: cursor) -> dict:
    "Fetches all earthquake types from RDS"
    return fetch_all(cursor, "types", "type_value", "type_id")


def get_or_add_id(value: str, all_items: dict, add_to_db_function) -> int:
    """Retrieves the ID for a given value, adding it to the database if not present"""
    if value in all_items:
        return all_items[value]
    new_id = add_to_db_function(value)
    if new_id is not None:
        all_items[value] = new_id
    return new_id


def add_network_to_db(conn: connection, cursor: cursor, network_value: str) -> int:
    """Adds the network value to the RDS"""
    query = """INSERT INTO networks (network_name) VALUES (%s) RETURNING network_id"""
    return execute_insert(conn, cursor, query, (network_value,))


def get_network_id(conn: connection, cursor: cursor, network_value: str, all_networks: dict) -> int:
    """Gets the network_id for the provided network"""
    return get_or_add_id(network_value, all_networks, lambda value_to_add: add_network_to_db(conn, cursor, value_to_add))


def add_magtype_to_db(conn: connection, cursor: cursor, magtype_value: str) -> int:
    """Adds the magType value to the RDS"""
    query = """INSERT INTO magtypes (magtype_value) VALUES (%s) RETURNING magtype_id"""
    return execute_insert(conn, cursor, query, (magtype_value,))


def get_magtype_id(conn: connection, cursor: cursor, magtype_value: str, all_magtypes: dict) -> int:
    """Gets the magtype_id for the provided magType value"""
    return get_or_add_id(magtype_value, all_magtypes, lambda value_to_add: add_magtype_to_db(conn, cursor, value_to_add))


def add_type_to_db(conn: connection, cursor: cursor, earthquake_type: str) -> int:
    """Adds the earthquake type to the RDS"""
    query = """INSERT INTO types (type_value) VALUES (%s) RETURNING type_id"""
    return execute_insert(conn, cursor, query, (earthquake_type,))


def get_type_id(conn: connection, cursor: cursor, earthquake_type: str, all_types: dict) -> int:
    """Gets the type_id for the provided earthquake type value"""
    return get_or_add_id(earthquake_type, all_types, lambda value_to_add: add_type_to_db(conn, cursor, value_to_add))


def add_earthquake_data_to_rds(conn: connection, cursor: cursor, earthquake_data: list[dict], all_alerts: dict, all_statuses: dict, all_networks: dict, all_magtypes: dict, all_types: dict) -> None:
    """Adds the provided data to the 'earthquakes' table"""
    try:
        for earthquake in earthquake_data:
            alert_id = all_alerts.get(earthquake.get(ALERT))
            status_id = all_statuses.get(earthquake["status"])
            network_id = get_network_id(
                conn, cursor, earthquake["network"], all_networks)
            magtype_id = get_magtype_id(
                conn, cursor, earthquake["magtype"], all_magtypes)
            type_id = get_type_id(
                conn, cursor, earthquake["earthquake_type"], all_types)

            cursor.execute("""INSERT INTO earthquakes (earthquake_id, alert_id, status_id, network_id, magtype_id, type_id, magnitude, lon, lat, depth, time, felt, cdi, mmi, significance, nst, dmin, gap, title)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """, (earthquake["earthquake_id"], alert_id, status_id, network_id, magtype_id, type_id,
                                  earthquake["magnitude"], earthquake["lon"], earthquake["lat"], earthquake["depth"],
                                  earthquake["time"], earthquake["felt"], earthquake["cdi"], earthquake["mmi"],
                                  earthquake["significance"], earthquake["nst"], earthquake["dmin"], earthquake["gap"], earthquake["title"]))

            conn.commit()
            logging.info(f"Successfully added earthquake {
                         earthquake['earthquake_id']} to the database")
    except (psycopg2.IntegrityError, psycopg2.OperationalError, psycopg2.DatabaseError) as e:
        logging.error(f"Database error: {e}")
        conn.rollback()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        conn.rollback()


if __name__ == "__main__":
    all_data = extract_process()
    transformed_data = transform_process(all_data)

    conn = get_connection(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, DB_PORT)
    if conn:
        cur = get_cursor(conn)
        if cur:
            all_alerts = get_all_alerts(cur)
            all_networks = get_all_networks(cur)
            all_statuses = get_all_statuses(cur)
            all_magtypes = get_all_magtypes(cur)
            all_types = get_all_types(cur)

            add_earthquake_data_to_rds(
                conn, cur, transformed_data, all_alerts, all_statuses, all_networks, all_magtypes, all_types)
