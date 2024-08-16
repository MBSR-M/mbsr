import functools
import logging
import time

from logging_config import Logger

logger = Logger(level=logging.DEBUG)


class Utils:
    @staticmethod
    def log_execution_time(func):
        """
        Static method to log the time taken by a function to execute.
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()  # Record the start time
            result = func(*args, **kwargs)  # Call the original function
            end_time = time.time()  # Record the end time
            execution_time = end_time - start_time  # Calculate the execution time
            logger.info(f"Function '{func.__name__}' took {execution_time:.4f} seconds to execute.")
            return result
        return wrapper

    @staticmethod
    def retry_on_exception(wait_time=1):
        """
        Static method to retry a function indefinitely on exceptions.
        Args:
        wait_time (int): Time to wait between retries in seconds.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                while True:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        logger.error(f"Exception occurred: {e}. Retrying in {wait_time} seconds...")
                        time.sleep(wait_time)
            return wrapper
        return decorator
