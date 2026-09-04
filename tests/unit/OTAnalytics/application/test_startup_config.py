"""Tests for startup configuration validation."""

import pytest

from OTAnalytics.application.startup_config import (
    InvalidTransferModeError,
    StartupConfigError,
    UnsupportedTransferModeError,
    validate_transfer_mode,
)
from OTAnalytics.domain.transfer_mode import TransferMode
from OTAnalytics.plugin_s3.config.parsing import (
    InvalidDurationError,
    MissingS3ConfigError,
)


class TestValidateTransferMode:
    def test_s3_mode_requires_the_web_ui(self) -> None:
        """CTk and the CLI do not implement S3 mode, so starting them is fatal.

        Falling back to local-filesystem silently would leave an S3-configured
        deployment quietly serving local files.

        # Requirement OP#10256
        """
        with pytest.raises(UnsupportedTransferModeError, match="--webui"):
            validate_transfer_mode(TransferMode.S3, start_webui=False)

    def test_s3_mode_with_web_ui_is_accepted(self) -> None:
        validate_transfer_mode(TransferMode.S3, start_webui=True)

    @pytest.mark.parametrize("start_webui", [True, False])
    def test_local_filesystem_is_accepted_by_every_front_end(
        self, start_webui: bool
    ) -> None:
        validate_transfer_mode(TransferMode.LOCAL_FILESYSTEM, start_webui=start_webui)

    def test_takes_a_mode_so_it_can_run_before_s3_parsing(self) -> None:
        """The check must not need parsed S3 settings.

        A CTk user in S3 mode with no credentials must be told that CTk cannot
        use S3, not which credentials are missing.

        # Requirement OP#10256
        """
        with pytest.raises(UnsupportedTransferModeError):
            validate_transfer_mode(TransferMode.S3, start_webui=False)


class TestStartupConfigErrorHierarchy:
    @pytest.mark.parametrize(
        "error",
        [
            UnsupportedTransferModeError("x"),
            InvalidTransferModeError("x"),
            InvalidDurationError("x"),
            MissingS3ConfigError(["bucket"]),
        ],
    )
    def test_every_misconfiguration_is_a_startup_config_error(
        self, error: Exception
    ) -> None:
        """One except clause must cover every way the config can be wrong.

        # Requirement OP#10256
        """
        assert isinstance(error, StartupConfigError)
