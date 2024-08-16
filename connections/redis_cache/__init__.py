import redis
import logging
import os
from dotenv import load_dotenv
from redis.exceptions import RedisError
from logging_config import Logger

# Load environment variables from .env file
load_dotenv()

logger = Logger(level=logging.DEBUG)


class RedisConnectionPool:
    def __init__(self):
        """
        Initialize the Redis connection pool with parameters from environment variables.
        """
        # Retrieve parameters from environment variables
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', 6379))
        db = int(os.getenv('REDIS_DB', 0))
        password = os.getenv('REDIS_PASSWORD', None)
        max_connections = int(os.getenv('REDIS_MAX_CONNECTIONS', 10))

        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
            # password=password,
            max_connections=max_connections
        )
        self.client = redis.Redis(connection_pool=self.pool)
        logger.info("Redis connection pool initialized.")

    def get_client(self):
        """
        Get a Redis client from the pool.

        Returns:
        redis.Redis: A Redis client instance.
        """
        try:
            return self.client
        except RedisError as e:
            logger.error(f"Error getting Redis client from pool: {e}")
            raise

    def set(self, key, value, ex=None):
        """
        Set a value in Redis.

        Args:
        key (str): The key to set.
        value (str): The value to set.
        ex (int): Expiration time in seconds (optional).
        """
        try:
            self.client.set(key, value, ex=ex)
            logger.info(f"Set key '{key}' in Redis.")
        except RedisError as e:
            logger.error(f"Error setting key '{key}' in Redis: {e}")
            raise

    def get(self, key):
        """
        Get a value from Redis.

        Args:
        key (str): The key to get.

        Returns:
        str: The value associated with the key.
        """
        try:
            value = self.client.get(key)
            logger.info(f"Got value for key '{key}' from Redis.")
            return value
        except RedisError as e:
            logger.error(f"Error getting key '{key}' from Redis: {e}")
            raise

    def delete(self, key):
        """
        Delete a key from Redis.

        Args:
        key (str): The key to delete.
        """
        try:
            self.client.delete(key)
            logger.info(f"Deleted key '{key}' from Redis.")
        except RedisError as e:
            logger.error(f"Error deleting key '{key}' from Redis: {e}")
            raise


redis_pool = RedisConnectionPool()
