"""This file is responsible for loading data into the RDS"""
# pylint: disable=W0718, W0621

import os
import logging

from psycopg2.extensions import connection, cursor
from psycopg2 import OperationalError
from dotenv import load_dotenv
import psycopg2.extras

load_dotenv()

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')

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
            "OperationalError occurred while trying to connect to the database: %s", e)
        return None
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
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
            "OperationalError occurred while trying to create a cursor: %s", e)
        return None
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        return None


def get_all_networks(cursor: cursor) -> dict:
    """Gets all networks in RDS"""
    formatted_networks = {}

    try:
        logging.info("Retrieving all networks from RDS")
        cursor.execute("""SELECT * FROM networks;""")
        networks = cursor.fetchall()
        for network in networks:
            formatted_networks[network["network_name"]] = network["network_id"]
        logging.info("Successfully fetched and formatted networks")
    except OperationalError as e:
        logging.error(
            "OperationalError occurred while fetching networks: %s", e)
        return formatted_networks
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        return formatted_networks

    return formatted_networks


def get_all_statuses(cursor: cursor) -> dict:
    """Gets all statuses in RDS"""
    formatted_statuses = {}

    try:
        logging.info("Retrieving all statuses from RDS")
        cursor.execute("""SELECT * FROM statuses;""")
        statuses = cursor.fetchall()
        for status in statuses:
            formatted_statuses[status["status_value"]] = status["status_id"]
        logging.info("Successfully fetched and formatted statuses")
    except OperationalError as e:
        logging.error(
            "OperationalError occurred while fetching networks: %s", e)
        return formatted_statuses
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        return formatted_statuses

    return formatted_statuses


def get_all_magtypes(cursor: cursor) -> dict:
    """Gets all magTypes in RDS"""
    formatted_magtypes = {}

    try:
        logging.info("Retrieving all magTypes from RDS")
        cursor.execute("""SELECT * FROM magtypes;""")
        magtypes = cursor.fetchall()
        for magtype in magtypes:
            formatted_magtypes[magtype["magtype_value"]
                               ] = magtype["magtype_id"]
        logging.info("Successfully fetched and formatted magTypes")
    except OperationalError as e:
        logging.error(
            "OperationalError occurred while fetching networks: %s", e)
        return formatted_magtypes
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        return formatted_magtypes

    return formatted_magtypes


def get_all_types(cursor: cursor) -> dict:
    """Gets all types in RDS"""
    formatted_types = {}

    try:
        logging.info("Retrieving all types from RDS")
        cursor.execute("""SELECT * FROM types;""")
        types = cursor.fetchall()
        for earthquake_type in types:
            formatted_types[earthquake_type["type_value"]
                            ] = earthquake_type["type_id"]
        logging.info("Successfully fetched and formatted types")
    except OperationalError as e:
        logging.error(
            "OperationalError occurred while fetching networks: %s", e)
        return formatted_types
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        return formatted_types

    return formatted_types


def add_network_to_db(conn: connection, cursor: cursor, network_value: str) -> int | None:
    """Adds provided network value to the RDS"""
    try:
        logging.info(f"Adding {network_value} to RDS")
        cursor.execute(
            """INSERT INTO networks (network_name) VALUES (%s) RETURNING network_id""", (network_value))
        new_id = cursor.fetchone()[0]
        conn.commit()
        logging.info(f"Added {network_value} to RDS")
        return new_id
    except psycopg2.IntegrityError as e:
        logging.error(f"Integrity error: {e}")
        conn.rollback()
        return None
    except psycopg2.OperationalError as e:
        logging.error(f"Operational error: {e}")
        conn.rollback()
        return None
    except psycopg2.DatabaseError as e:
        logging.error(f"Database error: {e}")
        conn.rollback()
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        conn.rollback()
        return None


def get_network_id(network_value: str, all_networks: dict) -> int | None:
    """Retrieves the associated network_id for a given network_value"""
    try:
        logging.info(f"Retrieving network_id for {network_value}")
        if network_value in all_networks:
            return all_networks[network_value]

        logging.info(f"network_name not present in database")
        new_id = add_network_to_db(network_value)

        if new_id is None:
            raise ValueError(f"Failed to add network {
                             network_value} to the database")

        all_networks[network_value] = new_id
        return new_id
    except KeyError as e:
        logging.error(f"Key error: {e}")
    except ValueError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    return None


def add_magtype_to_db(conn: connection, cursor: cursor, magtype_value: str) -> int | None:
    """Adds provided magtype value to the RDS"""
    try:
        logging.info(f"Adding {magtype_value} to RDS")
        cursor.execute(
            """INSERT INTO magtypes (magtype_value) VALUES (%s) RETURNING magtype_id""", (magtype_value))
        new_id = cursor.fetchone()[0]
        conn.commit()
        logging.info(f"Added {magtype_value} to RDS")
        return new_id
    except psycopg2.IntegrityError as e:
        logging.error(f"Integrity error: {e}")
        conn.rollback()
        return None
    except psycopg2.OperationalError as e:
        logging.error(f"Operational error: {e}")
        conn.rollback()
        return None
    except psycopg2.DatabaseError as e:
        logging.error(f"Database error: {e}")
        conn.rollback()
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        conn.rollback()
        return None


def get_magtype_id(magtype_value: str, all_magtypes: dict) -> int | None:
    """Retrieves the associated network_id for a given network_value"""
    try:
        logging.info(f"Retrieving magtype_id for {magtype_value}")
        if magtype_value in all_magtypes:
            return all_magtypes[magtype_value]

        logging.info(f"network_name not present in database")
        new_id = add_network_to_db(magtype_value)

        if new_id is None:
            raise ValueError(f"Failed to add network {
                             magtype_value} to the database")

        all_magtypes[magtype_value] = new_id
        return new_id
    except KeyError as e:
        logging.error(f"Key error: {e}")
    except ValueError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

    return None


def add_earthquake_data_to_rds(cursor: cursor, earthquake_data: list[dict], all_alerts: dict, all_statuses: dict) -> None:
    for earthquake in earthquake_data:
        alert_id = all_alerts[earthquake["alert"]]
        status_id = all_statuses[earthquake["status"]]
        network_id = get_network_id(earthquake_data["network"])
        magtype_id = get_magtype_id(earthquake_data["magtype"])

    sql_query = """INSERT INTO earthquakes (earthquake_id, alert_id, status_id, network_id, magtype_id, type_id, magnitude, lon, lat, depth, time, felt, cdi, mmi, significance, nst, dmin, gap, title)
                    values (%(earthquake_id)s)"""


if __name__ == "__main__":
    con = get_connection(DB_HOST, DB_NAME, DB_USERNAME, DB_PASSWORD, DB_PORT)
    cur = get_cursor(con)
