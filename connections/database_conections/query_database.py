import logging

from connections.database_conections import MySQLConnectionPool, close_connection

from logging_config import Logger

logger = Logger(level=logging.DEBUG)

# Initialize the connection pool once
connection_pool = MySQLConnectionPool(read=True)


# @read_only_decorator
def get_data(query):
    """
    Fetch data from the database using the given query.

    Args:
    query (str): The SQL query to execute.

    Returns:
    list: A list of tuples containing the query result.
    """
    try:
        conn = connection_pool.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return results
        finally:
            close_connection(conn)
    except Exception as e:
        logger.error(f"An error occurred while fetching data: {e}")
        return []
