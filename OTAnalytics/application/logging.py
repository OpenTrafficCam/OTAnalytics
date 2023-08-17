import logging
import sys
from datetime import datetime
from pathlib import Path

from OTAnalytics.application.config import LOG_DIR

LOGGER_NAME = "OTAnalytics"
LOG_NAME = f"{datetime.now().strftime(r'%Y-%m-%d_%H-%M-%S')}"
LOG_EXT = "log"
LOG_FILE = Path(LOG_DIR, f"{LOG_NAME}.{LOG_EXT}")
LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


def logger() -> logging.Logger:
    """Get logger.

    Returns:
        logging.Logger: the logger.
    """
    return logging.getLogger(LOGGER_NAME)


def set_log_level(log_level: int) -> None:
    logger().setLevel(log_level)


LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
    handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler(sys.stdout)],
)
