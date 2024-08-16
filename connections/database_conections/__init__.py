import logging
import os
from dotenv import load_dotenv
from mysql.connector import pooling, Error

from logging_config import Logger
from utils import Utils

# Load environment variables from .env file
load_dotenv()

# Initialize logger
logger = Logger(level=logging.DEBUG)


def close_connection(connection):
    """
    Close and return a connection to the pool.

    Args:
        connection (mysql.connector.connection.MySQLConnection): The connection to close.
    """
    if connection is None or not connection.is_connected():
        logger.warning("Attempted to close an invalid or already closed connection.")
        return

    try:
        connection.close()
        logger.info("Connection closed and returned to the pool.")
    except Error as error:
        logger.error(f"Error closing connection: {error}")
        raise


def _get_db_config(**db_config):
    """
    Get the database configuration with defaults from environment variables.

    Args:
        db_config (dict): Additional database configuration parameters.

    Returns:
        dict: The combined database configuration.
    """
    return {
        'user': os.getenv('DATABASE_USER'),
        'password': os.getenv('DATABASE_PASSWORD'),
        'host': os.getenv('DATABASE_HOST'),
        'database': os.getenv('DATABASE_NAME'),
        **db_config
    }


class MySQLConnectionPool:
    def __init__(self, pool_name=None, pool_size=None, read=False, write=False, **db_config):
        """
        Initialize the MySQLConnectionPool.

        Args:
            pool_name (str): The name of the connection pool. Defaults to environment variable 'DATABASE_POOL'.
            pool_size (int): The size of the connection pool. Defaults to environment variable 'DATABASE_POOL_SIZE'.
            read (bool): Flag to indicate if it's a read pool.
            write (bool): Flag to indicate if it's a write pool.
            db_config (dict): Database configuration parameters (user, password, host, database, etc.).
        """
        self.read = read
        self.write = write
        self.pool_name = pool_name or self._get_default_pool_name()
        self.pool_size = pool_size or int(os.getenv('DATABASE_POOL_SIZE', 5))
        self.db_config = _get_db_config(**db_config)

        self.pool = None
        self._create_pool()

    def _get_default_pool_name(self):
        """
        Determine the default pool name based on read/write flags.

        Returns:
            str: The default pool name.
        """
        if self.read:
            return os.getenv('DATABASE_POOL_READ', 'default_pool')
        if self.write:
            return os.getenv('DATABASE_POOL_WRITE', 'default_pool')
        return os.getenv('DATABASE_POOL', 'default_pool')

    @Utils.log_execution_time
    @Utils.retry_on_exception(wait_time=5)
    def _create_pool(self):
        """
        Create the connection pool and handle any errors.
        """
        try:
            self.pool = pooling.MySQLConnectionPool(
                pool_name=self.pool_name,
                pool_size=self.pool_size,
                pool_reset_session=True,
                **self.db_config
            )
            logger.info(f"Connection pool '{self.pool_name}' created with size {self.pool_size}.")
        except Error as e:
            logger.error(f"Error creating connection pool: {e}")
            raise

    @Utils.log_execution_time
    @Utils.retry_on_exception(wait_time=5)
    def get_connection(self):
        """
        Get a connection from the pool.

        Returns:
            mysql.connector.connection.MySQLConnection: A connection object.

        Raises:
            RuntimeError: If the pool is not initialized.
            Error: If there is an error getting a connection from the pool.
        """
        if self.pool is None:
            raise RuntimeError("Connection pool is not initialized.")

        try:
            connection = self.pool.get_connection()
            if connection.is_connected():
                logger.info("Successfully obtained a connection from the pool.")
            return connection
        except Error as error:
            logger.error(f"Error getting connection from pool: {error}")
            raise
