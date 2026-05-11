import functools
import inspect
from datetime import datetime
from typing import Any

from OTAnalytics.application.logger import logger


def log_processing_time(description: str) -> Any:
    def decorator_log_processing_time(function: Any) -> Any:
        @functools.wraps(function)
        async def async_log(*args: Any, **kwargs: Any) -> Any:
            start = datetime.now()
            result = await function(*args, **kwargs)
            end = datetime.now()
            duration = end - start
            logger().info(f"Finished processing {description} after {duration}")
            return result

        @functools.wraps(function)
        def sync_log(*args: Any, **kwargs: Any) -> Any:
            start = datetime.now()
            result = function(*args, **kwargs)
            end = datetime.now()
            duration = end - start
            logger().info(f"Finished processing {description} after {duration}")
            return result

        if inspect.iscoroutinefunction(function):
            return async_log
        else:
            return sync_log

    return decorator_log_processing_time
