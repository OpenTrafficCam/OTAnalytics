import functools
from datetime import datetime
from typing import Any

from OTAnalytics.application.logger import logger


def log_processing_time(description: str) -> Any:
    def decorator_log_processing_time(function: Any) -> Any:
        @functools.wraps(function)
        def log(*args: Any, **kwargs: Any) -> Any:
            start = datetime.now()
            function(*args, **kwargs)
            end = datetime.now()
            duration = end - start
            logger().info(f"Finished processing {description} after {duration}")

        return log

    return decorator_log_processing_time
