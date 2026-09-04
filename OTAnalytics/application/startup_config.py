"""Startup configuration selecting how OTAnalytics obtains tracks and videos."""

from dataclasses import dataclass

from OTAnalytics.application.s3_config import S3Config
from OTAnalytics.domain.transfer_mode import TransferMode


class StartupConfigError(Exception):
    """Base for startup misconfiguration.

    Startup config problems are operator errors, not defects, so they are
    reported as a message and a non-zero exit rather than a traceback. Catching
    this one type covers every way the configuration can be wrong.
    """


class UnsupportedTransferModeError(StartupConfigError):
    """Raised when the configured transfer mode cannot be served by the front-end."""


class InvalidTransferModeError(StartupConfigError):
    """Raised when the configured transfer mode is not a value OTAnalytics knows."""


@dataclass(frozen=True)
class StartupConfig:
    """How this OTAnalytics instance obtains its input files.

    Attributes:
        transfer_mode (TransferMode): where tracks and videos come from.
        s3 (S3Config | None): S3 settings, present only in S3 mode.
    """

    transfer_mode: TransferMode
    s3: S3Config | None = None

    @property
    def uses_s3(self) -> bool:
        return self.transfer_mode == TransferMode.S3


def validate_transfer_mode(mode: TransferMode, start_webui: bool) -> None:
    """Fail fast when the configured transfer mode cannot be served.

    S3 mode is only implemented for the NiceGUI web UI. Falling back to the
    local filesystem silently would leave an S3-configured deployment quietly
    serving local files, which is hard to diagnose.

    Takes the mode rather than a whole `StartupConfig` on purpose: the caller
    must be able to run this check *before* the S3 settings are parsed.
    Otherwise a CTk user in S3 mode with incomplete credentials is told which
    settings are missing, when the real problem is that their front-end cannot
    use S3 at all.

    Args:
        mode (TransferMode): the configured transfer mode.
        start_webui (bool): whether the web UI is the front-end being started.

    Raises:
        UnsupportedTransferModeError: if S3 mode is configured for a front-end
            that does not support it.
    """
    if mode == TransferMode.S3 and not start_webui:
        raise UnsupportedTransferModeError(
            f"data-transfer-mode '{TransferMode.S3.value}' is only supported "
            "with --webui. Either start OTAnalytics with --webui or set "
            f"data-transfer-mode to '{TransferMode.LOCAL_FILESYSTEM.value}'."
        )
