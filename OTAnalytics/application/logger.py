import logging
import sys
from datetime import datetime
from pathlib import Path

from OTAnalytics.application.config import DEFAULT_LOG_DIR

LOGGER_NAME = "OTAnalytics"
DEFAULT_LOG_NAME = f"{datetime.now().strftime(r'%Y-%m-%d_%H-%M-%S')}"
LOG_EXT = "log"
DEFAULT_LOG_FILE = Path(DEFAULT_LOG_DIR, f"{DEFAULT_LOG_NAME}.{LOG_EXT}")
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"


class LogFileAlreadyExists(Exception):
    pass


def logger() -> logging.Logger:
    """Get logger.

    Returns:
        logging.Logger: the logger.
    """
    return logging.getLogger(LOGGER_NAME)


def setup_logger(
    log_file: Path = DEFAULT_LOG_FILE,
    log_level: int = logging.INFO,
    log_format: str = LOG_FORMAT,
    date_format: str = LOG_DATE_FORMAT,
    overwrite: bool = False,
) -> None:
    if log_file.exists() and not overwrite:
        raise LogFileAlreadyExists(
            f"Log file '{log_file}' already exists. "
            "Please specify option to overwrite the log file when using the CLI."
        )
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.touch()
    logging.basicConfig(
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, mode="w"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logger().setLevel(log_level)
