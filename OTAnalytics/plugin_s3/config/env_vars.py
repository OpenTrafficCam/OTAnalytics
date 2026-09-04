import os
from dataclasses import dataclass, field

ENV_DATA_TRANSFER_MODE = "DATA_TRANSFER_MODE"
ENV_S3_ENDPOINT_URL = "S3_ENDPOINT_URL"
ENV_S3_ACCESS_KEY = "S3_ACCESS_KEY"
ENV_S3_SECRET_KEY = "S3_SECRET_KEY"  # nosec B105 - variable name, not a secret
ENV_S3_BUCKET = "S3_BUCKET"
ENV_S3_REGION = "S3_REGION"
ENV_S3_KEY_PREFIX = "S3_KEY_PREFIX"
ENV_S3_USER_SOURCE = "S3_USER_SOURCE"
ENV_S3_MAX_LOAD_DURATION = "S3_MAX_LOAD_DURATION"
ENV_S3_DOWNLOAD_CONCURRENCY = "S3_DOWNLOAD_CONCURRENCY"


@dataclass
class S3Env:
    """S3 settings read from the environment.

    Values are read when the instance is constructed. Names for the first six
    fields match OTCloud's `S3Env` so a deployment already configured for
    OTCloud needs no new variables; the remainder are specific to OTAnalytics.

    Every field is optional here — whether a missing value is fatal depends on
    the configured transfer mode, which startup validation decides.
    """

    endpoint_url: str | None = field(
        default_factory=lambda: os.environ.get(ENV_S3_ENDPOINT_URL, None)
    )
    access_key: str | None = field(
        default_factory=lambda: os.environ.get(ENV_S3_ACCESS_KEY, None)
    )
    secret_key: str | None = field(
        default_factory=lambda: os.environ.get(ENV_S3_SECRET_KEY, None)
    )
    bucket: str | None = field(
        default_factory=lambda: os.environ.get(ENV_S3_BUCKET, None)
    )
    region: str | None = field(
        default_factory=lambda: os.environ.get(ENV_S3_REGION, None)
    )
    key_prefix: str | None = field(
        default_factory=lambda: os.environ.get(ENV_S3_KEY_PREFIX, None)
    )
    user_source: str | None = field(
        default_factory=lambda: os.environ.get(ENV_S3_USER_SOURCE, None)
    )
    max_load_duration: str | None = field(
        default_factory=lambda: os.environ.get(ENV_S3_MAX_LOAD_DURATION, None)
    )
    download_concurrency: str | None = field(
        default_factory=lambda: os.environ.get(ENV_S3_DOWNLOAD_CONCURRENCY, None)
    )


def transfer_mode_from_env() -> str | None:
    """Read the configured transfer mode from the environment.

    Returns:
        str | None: the raw value of DATA_TRANSFER_MODE, or None if unset.
    """
    return os.environ.get(ENV_DATA_TRANSFER_MODE, None)
