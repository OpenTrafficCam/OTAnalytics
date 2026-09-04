"""Build the S3 configuration from environment variables.

S3 access is configured entirely through the environment. Ten flat settings, two
of them secrets, six already carrying OTCloud's variable names — a config file
would be machinery without structure to justify it, and secrets passed as CLI
flags appear in `ps`. See `docs/adr/0003-configure-s3-via-environment.md`.
"""

import re
from datetime import timedelta

from OTAnalytics.application.startup_config import StartupConfigError
from OTAnalytics.plugin_s3.config.env_vars import (
    ENV_S3_ACCESS_KEY,
    ENV_S3_BUCKET,
    ENV_S3_KEY_PREFIX,
    ENV_S3_SECRET_KEY,
    ENV_S3_USER_SOURCE,
    S3Env,
)
from OTAnalytics.plugin_s3.config.s3 import (
    DEFAULT_DOWNLOAD_CONCURRENCY,
    DEFAULT_MAX_LOAD_DURATION,
    S3Config,
)

DURATION_PATTERN = re.compile(r"^(\d+)([hms])$")
_UNIT_TO_KEYWORD = {"h": "hours", "m": "minutes", "s": "seconds"}


class InvalidDurationError(StartupConfigError):
    """Raised when a duration string cannot be parsed."""


class MissingS3ConfigError(StartupConfigError):
    """Raised when required S3 environment variables are not set.

    Names every missing variable rather than only the first, so an operator can
    fix them in one pass instead of one restart per variable.

    Attributes:
        missing (list[str]): the environment variables that were not set.
    """

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(
            "Missing required S3 configuration. Set these environment variables: "
            + ", ".join(missing)
            + "."
        )


def parse_duration(value: str) -> timedelta:
    """Parse a duration such as `10h`, `45m` or `90s`.

    A unit suffix is required. Without one, `10` would silently be read as
    either seconds or hours depending on the reader's assumption.

    Args:
        value (str): the duration string.

    Returns:
        timedelta: the parsed duration.

    Raises:
        InvalidDurationError: if the value is not a whole number followed by
            `h`, `m` or `s`.
    """
    match = DURATION_PATTERN.match(value.strip())
    if not match:
        raise InvalidDurationError(
            f"Cannot parse duration '{value}'. "
            "Expected a whole number followed by 'h', 'm' or 's', for example '10h'."
        )
    amount, unit = match.groups()
    return timedelta(**{_UNIT_TO_KEYWORD[unit]: int(amount)})


def parse_s3_config(env: S3Env) -> S3Config:
    """Build the S3 configuration from environment values.

    Args:
        env (S3Env): the S3 environment variables.

    Returns:
        S3Config: the parsed configuration.

    Raises:
        MissingS3ConfigError: if required variables are unset. Every missing
            variable is reported, not just the first.
        InvalidDurationError: if S3_MAX_LOAD_DURATION is malformed.
    """
    required = (
        (ENV_S3_ACCESS_KEY, env.access_key),
        (ENV_S3_SECRET_KEY, env.secret_key),
        (ENV_S3_BUCKET, env.bucket),
        (ENV_S3_KEY_PREFIX, env.key_prefix),
        (ENV_S3_USER_SOURCE, env.user_source),
    )
    if missing := [name for name, value in required if value is None]:
        raise MissingS3ConfigError(missing)

    return S3Config(
        endpoint_url=env.endpoint_url,
        access_key=_required(env.access_key),
        secret_key=_required(env.secret_key),
        bucket=_required(env.bucket),
        region=env.region,
        key_prefix=_required(env.key_prefix),
        user_source=_required(env.user_source),
        max_load_duration=_parse_max_load_duration(env),
        download_concurrency=_parse_download_concurrency(env),
    )


def _required(value: str | None) -> str:
    """Narrow a value the missing-variable check has already guaranteed."""
    if value is None:  # pragma: no cover - guarded by parse_s3_config
        raise MissingS3ConfigError([])
    return value


def _parse_max_load_duration(env: S3Env) -> timedelta:
    if env.max_load_duration is None:
        return DEFAULT_MAX_LOAD_DURATION
    return parse_duration(env.max_load_duration)


def _parse_download_concurrency(env: S3Env) -> int:
    if env.download_concurrency is None:
        return DEFAULT_DOWNLOAD_CONCURRENCY
    return int(env.download_concurrency)
