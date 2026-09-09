"""Validation of how OTAnalytics was configured at startup.

Deliberately free of any S3 type. Only the transfer mode — a domain concept —
reaches this layer; everything specific to a mode lives in that mode's plugin.
"""

from OTAnalytics.domain.transfer_mode import TransferMode


class StartupConfigError(Exception):
    """Base for startup misconfiguration.

    Startup config problems are operator errors, not defects, so they are
    reported as a message and a clean exit rather than a traceback. Catching
    this one type covers every way the configuration can be wrong, including
    the mode-specific subclasses raised from plugins.
    """


class UnsupportedTransferModeError(StartupConfigError):
    """Raised when the configured transfer mode cannot be served by the front-end."""


class InvalidTransferModeError(StartupConfigError):
    """Raised when the configured transfer mode is not a value OTAnalytics knows."""


def validate_transfer_mode(mode: TransferMode, start_webui: bool) -> None:
    """Fail fast when the configured transfer mode cannot be served.

    S3 mode is only implemented for the NiceGUI web UI. Falling back to the
    local filesystem silently would leave an S3-configured deployment quietly
    serving local files, which is hard to diagnose.

    Takes the mode rather than a fully parsed configuration on purpose: the
    caller must be able to run this check *before* any mode-specific settings
    are read. Otherwise a CTk user in S3 mode with incomplete credentials is
    told which settings are missing, when the real problem is that their
    front-end cannot use S3 at all.

    Args:
        mode (TransferMode): the configured transfer mode.
        start_webui (bool): whether the web UI is the front-end being started.

    Raises:
        UnsupportedTransferModeError: if S3 mode is configured for a front-end
            that does not support it.
    """
    if mode == TransferMode.S3 and not start_webui:
        raise UnsupportedTransferModeError(
            f"DATA_TRANSFER_MODE '{TransferMode.S3.value}' is only supported "
            "with --webui. Either start OTAnalytics with --webui or set "
            f"DATA_TRANSFER_MODE to '{TransferMode.LOCAL_FILESYSTEM.value}'."
        )
