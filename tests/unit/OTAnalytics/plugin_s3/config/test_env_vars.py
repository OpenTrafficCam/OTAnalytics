"""Tests for reading the transfer mode from the environment."""

import pytest

from OTAnalytics.application.startup_config import InvalidTransferModeError
from OTAnalytics.domain.transfer_mode import TransferMode
from OTAnalytics.plugin_s3.config.env_vars import transfer_mode_from_env


class TestTransferModeFromEnv:
    def test_unset_defaults_to_local_filesystem(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The default path must behave exactly as before this epic.

        # Requirement OP#10256
        """
        monkeypatch.delenv("DATA_TRANSFER_MODE", raising=False)

        assert transfer_mode_from_env() == TransferMode.LOCAL_FILESYSTEM

    @pytest.mark.parametrize(
        "value, expected",
        [
            ("local-filesystem", TransferMode.LOCAL_FILESYSTEM),
            ("s3", TransferMode.S3),
        ],
    )
    def test_reads_supported_values(
        self, monkeypatch: pytest.MonkeyPatch, value: str, expected: TransferMode
    ) -> None:
        monkeypatch.setenv("DATA_TRANSFER_MODE", value)

        assert transfer_mode_from_env() == expected

    def test_unsupported_value_names_what_is_supported(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """OTCloud defines an ftp mode and may share a machine with OTAnalytics.

        # Requirement OP#10256
        """
        monkeypatch.setenv("DATA_TRANSFER_MODE", "ftp")

        with pytest.raises(InvalidTransferModeError, match="local-filesystem"):
            transfer_mode_from_env()
