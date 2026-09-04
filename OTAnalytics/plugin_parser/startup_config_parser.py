"""Parse the OTAnalytics startup configuration file.

The startup config is deliberately separate from the otconfig: an otconfig is a
per-project file that users save and share, and S3 credentials must not end up
in one. See `docs/adr/0003-yaml-startup-config-with-env-override.md`.
"""

from pathlib import Path

import yaml

from OTAnalytics.application.startup_config import (
    InvalidTransferModeError,
    StartupConfig,
    StartupConfigError,
)
from OTAnalytics.domain.transfer_mode import TransferMode
from OTAnalytics.plugin_s3.config.env_vars import S3Env
from OTAnalytics.plugin_s3.config.parsing import parse_s3_config

DATA_TRANSFER_MODE = "data-transfer-mode"
S3_SECTION = "s3"


def parse_transfer_mode(
    file: Path | None, mode_from_env: str | None = None
) -> TransferMode:
    """Read only the transfer mode, without touching the S3 settings.

    Separate from `parse_startup_config` so the front-end compatibility check
    can run before S3 parsing, which may itself fail for unrelated reasons.

    Args:
        file (Path | None): path to the startup config, or None if none was given.
        mode_from_env (str | None): value of DATA_TRANSFER_MODE, if set.

    Returns:
        TransferMode: the configured mode, defaulting to local-filesystem.

    Raises:
        FileNotFoundError: if `file` is given but does not exist.
        ValueError: if the configured transfer mode is not supported.
    """
    return _to_transfer_mode(
        _first_set(mode_from_env, _read(file).get(DATA_TRANSFER_MODE, None))
    )


def parse_startup_config(
    file: Path | None,
    mode_from_env: str | None = None,
    env: S3Env | None = None,
) -> StartupConfig:
    """Parse the startup configuration.

    Environment values take precedence over file values, so a deployment can
    keep secrets out of the file entirely — or omit the file altogether and
    configure everything through the environment.

    Args:
        file (Path | None): path to the startup config, or None if none was given.
        mode_from_env (str | None): value of DATA_TRANSFER_MODE, if set.
        env (S3Env | None): S3 environment values. Read from the environment
            when omitted.

    Returns:
        StartupConfig: the parsed configuration. Defaults to local-filesystem.

    Raises:
        FileNotFoundError: if `file` is given but does not exist.
        ValueError: if the configured transfer mode is not supported.
        MissingS3ConfigError: in S3 mode, if required settings are absent from
            both the file and the environment.
        InvalidDurationError: if `max-load-duration` is malformed.
    """
    data = _read(file)
    resolved_env = env if env is not None else S3Env()

    transfer_mode = _to_transfer_mode(
        _first_set(mode_from_env, data.get(DATA_TRANSFER_MODE, None))
    )

    if transfer_mode != TransferMode.S3:
        return StartupConfig(transfer_mode=transfer_mode, s3=None)

    # An absent section is passed as empty rather than skipped, so a deployment
    # can supply every setting through the environment and still have any
    # genuinely missing ones reported together.
    return StartupConfig(
        transfer_mode=transfer_mode,
        s3=parse_s3_config(data.get(S3_SECTION, {}) or {}, resolved_env),
    )


def _to_transfer_mode(raw_mode: str | None) -> TransferMode:
    if raw_mode is None:
        return TransferMode.LOCAL_FILESYSTEM
    try:
        return TransferMode(raw_mode)
    except ValueError:
        supported = ", ".join(f"'{mode.value}'" for mode in TransferMode)
        raise InvalidTransferModeError(
            f"Unsupported {DATA_TRANSFER_MODE} '{raw_mode}'. "
            f"Supported values are {supported}."
        ) from None


def _read(file: Path | None) -> dict:
    if file is None:
        return {}
    if not file.exists():
        raise StartupConfigError(f"Startup config file '{file}' does not exist.")
    content = yaml.safe_load(file.read_text())
    return content if isinstance(content, dict) else {}


def _first_set(*values: str | None) -> str | None:
    """First value that was actually supplied.

    Uses `is not None` rather than truthiness so an intentionally empty value —
    `S3_KEY_PREFIX=""` to read from the root of a bucket — counts as supplied
    instead of silently falling through to the file.
    """
    for value in values:
        if value is not None:
            return value
    return None
