"""Parse the `s3` block of the startup configuration.

Environment variables take precedence over file values, mirroring OTCloud's
`parse_s3_config(data, env)`. OTCloud exposes this as a mixin because several of
its parsers need it; OTAnalytics has a single startup config parser, so a plain
function is used instead.
"""

import re
from datetime import timedelta

from OTAnalytics.application.s3_config import (
    DEFAULT_DOWNLOAD_CONCURRENCY,
    DEFAULT_MAX_LOAD_DURATION,
    S3Config,
)
from OTAnalytics.application.startup_config import StartupConfigError
from OTAnalytics.plugin_s3.config.env_vars import S3Env

DURATION_PATTERN = re.compile(r"^(\d+)([hms])$")
_UNIT_TO_KEYWORD = {"h": "hours", "m": "minutes", "s": "seconds"}


class InvalidDurationError(StartupConfigError):
    """Raised when a duration string cannot be parsed."""


class MissingS3ConfigError(StartupConfigError):
    """Raised when required S3 settings are absent from both file and environment.

    Carries every missing field rather than only the first, so an operator can
    fix them in one pass instead of one restart per field.

    Attributes:
        missing (list[str]): the config keys that were not supplied.
    """

    def __init__(self, missing: list[str]) -> None:
        self.missing = missing
        super().__init__(
            "Missing required S3 configuration: "
            + ", ".join(missing)
            + ". Supply them in the startup config's 's3' block or via the "
            "corresponding S3_* environment variables."
        )


class S3ConfigKeys:
    S3 = "s3"
    ENDPOINT_URL = "endpoint-url"
    ACCESS_KEY = "access-key"
    SECRET_KEY = "secret-key"  # nosec B105 - config key name, not a secret
    BUCKET = "bucket"
    REGION = "region"
    KEY_PREFIX = "key-prefix"
    USER_SOURCE = "user-source"
    MAX_LOAD_DURATION = "max-load-duration"
    DOWNLOAD_CONCURRENCY = "download-concurrency"


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


def parse_s3_config(section: dict, env: S3Env) -> S3Config:
    """Parse the `s3` section of a startup configuration.

    Args:
        section (dict): the contents of the `s3` block. May be empty, in which
            case every setting must come from the environment.
        env (S3Env): environment values, which take precedence over the file.

    Returns:
        S3Config: the parsed configuration.

    Raises:
        MissingS3ConfigError: if required keys are absent from both the file and
            the environment. Every missing key is reported, not just the first.
        InvalidDurationError: if `max-load-duration` is malformed.
    """
    resolved = _resolve_required(section, env)

    return S3Config(
        endpoint_url=_resolve(env.endpoint_url, section, S3ConfigKeys.ENDPOINT_URL),
        access_key=resolved[S3ConfigKeys.ACCESS_KEY],
        secret_key=resolved[S3ConfigKeys.SECRET_KEY],
        bucket=resolved[S3ConfigKeys.BUCKET],
        region=_resolve(env.region, section, S3ConfigKeys.REGION),
        key_prefix=resolved[S3ConfigKeys.KEY_PREFIX],
        user_source=resolved[S3ConfigKeys.USER_SOURCE],
        max_load_duration=_parse_max_load_duration(section, env),
        download_concurrency=_parse_download_concurrency(section, env),
    )


def _resolve_required(section: dict, env: S3Env) -> dict[str, str]:
    """Resolve the settings that have no default, reporting all absentees.

    Returns:
        dict[str, str]: every required key, guaranteed present.

    Raises:
        MissingS3ConfigError: naming every key absent from file and environment.
    """
    required = (
        (S3ConfigKeys.ACCESS_KEY, env.access_key),
        (S3ConfigKeys.SECRET_KEY, env.secret_key),
        (S3ConfigKeys.BUCKET, env.bucket),
        (S3ConfigKeys.KEY_PREFIX, env.key_prefix),
        (S3ConfigKeys.USER_SOURCE, env.user_source),
    )
    resolved = {key: _resolve(from_env, section, key) for key, from_env in required}
    if missing := [key for key, value in resolved.items() if value is None]:
        raise MissingS3ConfigError(missing)
    return {key: value for key, value in resolved.items() if value is not None}


def _resolve(from_env: str | None, section: dict, key: str) -> str | None:
    """Environment value if supplied, otherwise the file value.

    Compares against None rather than using `or`, so an intentionally empty
    setting — `S3_KEY_PREFIX=""` to read from the root of a bucket — counts as
    supplied instead of silently falling back to the file.
    """
    if from_env is not None:
        return from_env
    return section.get(key, None)


def _parse_max_load_duration(section: dict, env: S3Env) -> timedelta:
    value = _resolve(env.max_load_duration, section, S3ConfigKeys.MAX_LOAD_DURATION)
    if value is None:
        return DEFAULT_MAX_LOAD_DURATION
    return parse_duration(str(value))


def _parse_download_concurrency(section: dict, env: S3Env) -> int:
    value = _resolve(
        env.download_concurrency, section, S3ConfigKeys.DOWNLOAD_CONCURRENCY
    )
    if value is None:
        return DEFAULT_DOWNLOAD_CONCURRENCY
    return int(value)
