import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

LOGS_DIRECTORY = os.getenv('LOGS_DIRECTORY')


class Logger:
    _log_dir = None

    def __init__(self, log_dir: str = "logs", level: int = logging.DEBUG):
        self.log_dir = log_dir
        log_dir = LOGS_DIRECTORY
        """
        Initialize the Logger instance.

        Args:
        log_dir (str): The centralized directory where the log files will be stored.
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG).
        """
        # Set the centralized log directory
        if Logger._log_dir is None:
            Logger._log_dir = log_dir
            os.makedirs(Logger._log_dir, exist_ok=True)

        # Get the current date for log file names
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Set the full paths for the log files
        general_log_file = f"general-{current_date}.log"
        error_log_file = f"error-{current_date}.log"

        general_log_path = os.path.join(Logger._log_dir, general_log_file)
        error_log_path = os.path.join(Logger._log_dir, error_log_file)

        # Configure the logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)

        # File handler for general logs
        general_file_handler = logging.FileHandler(general_log_path)
        general_file_handler.setLevel(level)
        general_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

        # File handler for error logs
        error_file_handler = logging.FileHandler(error_log_path)
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

        # Stream handler for console output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

        # Add handlers to the logger
        self.logger.addHandler(general_file_handler)
        self.logger.addHandler(error_file_handler)
        self.logger.addHandler(console_handler)

        # Call method to clean up old logs
        self._cleanup_old_logs()

    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)

    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)

    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log a critical message."""
        self.logger.critical(message)

    def _cleanup_old_logs(self):
        """
        Delete log files older than 7 days.
        """
        now = datetime.now()
        retention_period = timedelta(days=7)

        for filename in os.listdir(Logger._log_dir):
            file_path = os.path.join(Logger._log_dir, filename)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                if now - file_time > retention_period:
                    logging.info(f"Deleting old log file: {filename}")
                    os.remove(file_path)
