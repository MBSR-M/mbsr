import logging
import re

from connections.database_conections import MySQLConnectionPool, close_connection
from logging_config import Logger

# Initialize the logger
logger = Logger(level=logging.DEBUG)

# Initialize the connection pool once
connection_pool = MySQLConnectionPool(write=True)


def validate_identifier(identifier):
    """
    Validate that the identifier (table name or column name) only contains
    alphanumeric characters and underscores.

    Args:
        identifier (str): The identifier to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', identifier))


def insert_data(table_name, data):
    """
    Insert data into the specified table.

    Args:
        table_name (str): The name of the table to insert data into.
        data (dict): A dictionary where keys are column names and values are the data to be inserted.

    Returns:
        bool: True if the insertion was successful, False otherwise.
    """
    if not validate_identifier(table_name) or not all(validate_identifier(col) for col in data.keys()):
        logger.error("Invalid table name or column names.")
        return False

    # Build the SQL query dynamically
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s'] * len(data))
    sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
    values = list(data.values())

    try:
        # Get the connection from the pool
        conn = connection_pool.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, values)
                conn.commit()  # Commit the transaction
                logger.info(f"Data inserted successfully into {table_name}.")
                return True
        except Exception as e:
            logger.error(f"Error inserting data into {table_name}: {e}")
            conn.rollback()  # Rollback the transaction in case of error
            return False
        finally:
            close_connection(conn)
    except Exception as e:
        logger.error(f"An error occurred while connecting to the database: {e}")
        return False
