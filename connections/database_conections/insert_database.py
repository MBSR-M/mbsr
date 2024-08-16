import logging
import re

from connections.database_conections import MySQLConnectionPool, close_connection
from logging_config import Logger

# Initialize the logger
logger = Logger(level=logging.DEBUG)

# Initialize the connection pool once
connection_pool = MySQLConnectionPool(write=True)


def insert_data(table_name, data):
    """
    Insert data into the specified table.

    Args:
    table_name (str): The name of the table to insert data into.
    data (dict): A dictionary where keys are column names and values are the data to be inserted.

    Returns:
    bool: True if the insertion was successful, False otherwise.
    """
    # Build the SQL query dynamically
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['%s'] * len(data))
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    values = list(data.values())

    try:
        # Get the connection from the pool
        conn = connection_pool.get_connection()
        try:
            cursor = conn.cursor()
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

