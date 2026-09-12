import os
from dataclasses import dataclass, field
from typing import Callable

from OTAnalytics.application.startup_config import InvalidTransferModeError
from OTAnalytics.domain.transfer_mode import TransferMode

ENV_DATA_TRANSFER_MODE = "OTA_DATA_TRANSFER_MODE"
ENV_S3_ENDPOINT_URL = "OTA_S3_ENDPOINT_URL"
ENV_S3_ACCESS_KEY = "OTA_S3_ACCESS_KEY"
ENV_S3_SECRET_KEY = "OTA_S3_SECRET_KEY"  # nosec B105 - variable name, not a secret
ENV_S3_BUCKET = "OTA_S3_BUCKET"
ENV_S3_REGION = "OTA_S3_REGION"
ENV_S3_USER_SOURCE = "OTA_S3_USER_SOURCE"
ENV_S3_MAX_LOAD_DURATION = "OTA_S3_MAX_LOAD_DURATION"
ENV_S3_DOWNLOAD_CONCURRENCY = "OTA_S3_DOWNLOAD_CONCURRENCY"


def read_env_var(var_name: str) -> str | None:
    return os.environ.get(var_name, None)


def _make_env_reader(var_name: str) -> Callable[[], str | None]:
    return lambda: read_env_var(var_name)


@dataclass
class S3Env:
    """S3 settings read from the environment.

    Values are read when the instance is constructed.
    Every field is optional here — whether a missing value is fatal depends on
    the configured transfer mode, which startup validation decides.
    """

    endpoint_url: str | None = field(
        default_factory=_make_env_reader(ENV_S3_ENDPOINT_URL)
    )
    access_key: str | None = field(default_factory=_make_env_reader(ENV_S3_ACCESS_KEY))
    secret_key: str | None = field(default_factory=_make_env_reader(ENV_S3_SECRET_KEY))
    bucket: str | None = field(default_factory=_make_env_reader(ENV_S3_BUCKET))
    region: str | None = field(default_factory=_make_env_reader(ENV_S3_REGION))
    user_source: str | None = field(
        default_factory=_make_env_reader(ENV_S3_USER_SOURCE)
    )
    max_load_duration: str | None = field(
        default_factory=_make_env_reader(ENV_S3_MAX_LOAD_DURATION)
    )
    download_concurrency: str | None = field(
        default_factory=_make_env_reader(ENV_S3_DOWNLOAD_CONCURRENCY)
    )


def transfer_mode_from_env() -> TransferMode:
    """Read the configured transfer mode from the environment.

    Returns:
        TransferMode: the configured mode, defaulting to local-filesystem when
            DATA_TRANSFER_MODE is unset.

    Raises:
        InvalidTransferModeError: if the value is not one OTAnalytics supports.
            The message lists the supported values, because OTCloud defines an
            `ftp` mode that OTAnalytics does not and the two may share a machine.
    """
    raw_mode = read_env_var(ENV_DATA_TRANSFER_MODE)
    if raw_mode is None:
        return TransferMode.LOCAL_FILESYSTEM
    try:
        return TransferMode(raw_mode)
    except ValueError:
        supported = ", ".join(f"'{mode.value}'" for mode in TransferMode)
        raise InvalidTransferModeError(
            f"Unsupported {ENV_DATA_TRANSFER_MODE} '{raw_mode}'. "
            f"Supported values are {supported}."
        ) from None
