"""Environments for the application started as a subprocess in tests.

The application is configured by environment variables only, so a test that
starts it inherits whatever the developer's shell exports. A machine set up for
s3 work exports `OTA_DATA_TRANSFER_MODE=s3`, which silently starts the
local-mode tests in s3 mode and makes them fail. Tests therefore state the
environment they want instead of inheriting one.
"""

import os

from OTAnalytics.plugin_s3.config.env_vars import (
    ENV_DATA_TRANSFER_MODE,
    ENV_S3_ACCESS_KEY,
    ENV_S3_BUCKET,
    ENV_S3_DOWNLOAD_CONCURRENCY,
    ENV_S3_ENDPOINT_URL,
    ENV_S3_MAX_LOAD_DURATION,
    ENV_S3_REGION,
    ENV_S3_SECRET_KEY,
    ENV_S3_USER_SOURCE,
)

TRANSFER_MODE_VARIABLES = (
    ENV_DATA_TRANSFER_MODE,
    ENV_S3_ENDPOINT_URL,
    ENV_S3_ACCESS_KEY,
    ENV_S3_SECRET_KEY,
    ENV_S3_BUCKET,
    ENV_S3_REGION,
    ENV_S3_USER_SOURCE,
    ENV_S3_MAX_LOAD_DURATION,
    ENV_S3_DOWNLOAD_CONCURRENCY,
)


def local_filesystem_environment() -> dict[str, str]:
    """The current environment with every transfer mode setting removed.

    Everything else is kept, because the application still needs PATH, HOME and
    whatever else the interpreter was started with.

    Returns:
        dict[str, str]: environment configuring the local filesystem mode.
    """
    return {
        name: value
        for name, value in os.environ.items()
        if name not in TRANSFER_MODE_VARIABLES
    }


def s3_environment(settings: dict[str, str]) -> dict[str, str]:
    """The current environment configured for s3 mode by `settings` alone.

    Starting from `local_filesystem_environment` means a variable the shell
    happens to export cannot reach the application unless the test names it.

    Args:
        settings: the transfer mode variables this test wants to set.

    Returns:
        dict[str, str]: environment configuring s3 mode.
    """
    environment = local_filesystem_environment()
    environment.update(settings)
    return environment
