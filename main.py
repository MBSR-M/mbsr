import logging

from connections.database_conections.query_database import get_data
from logging_config import Logger

logger = Logger(level=logging.DEBUG)


def main():
    try:
        logger.info("Fetching data from database...")
        data = get_data("SELECT * FROM user_details;")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
