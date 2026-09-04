"""Tests for parsing the OTAnalytics startup configuration file."""

from datetime import timedelta
from pathlib import Path

import pytest
import yaml

from OTAnalytics.application.startup_config import (
    InvalidTransferModeError,
    StartupConfigError,
)
from OTAnalytics.domain.transfer_mode import TransferMode
from OTAnalytics.plugin_parser.startup_config_parser import (
    parse_startup_config,
    parse_transfer_mode,
)
from OTAnalytics.plugin_s3.config.env_vars import S3Env
from OTAnalytics.plugin_s3.config.parsing import MissingS3ConfigError

S3_BLOCK = {
    "endpoint-url": "http://localhost:9000",
    "access-key": "minioadmin",
    "secret-key": "minioadmin",  # gitleaks:allow
    "bucket": "otcloud",
    "key-prefix": "6-1145/site/OTCamera19/",
    "user-source": "/data/otanalytics-source",
    "max-load-duration": "10h",
}


def empty_env() -> S3Env:
    return S3Env(
        endpoint_url=None,
        access_key=None,
        secret_key=None,
        bucket=None,
        region=None,
        key_prefix=None,
        user_source=None,
        max_load_duration=None,
        download_concurrency=None,
    )


def write_config(tmp_path: Path, content: dict) -> Path:
    file = tmp_path / "startup.yaml"
    file.write_text(yaml.safe_dump(content))
    return file


class TestParseStartupConfig:
    def test_no_file_defaults_to_local_filesystem(self) -> None:
        """The default path must behave exactly as before this epic.

        # Requirement OP#10256
        """
        actual = parse_startup_config(None, mode_from_env=None, env=empty_env())

        assert actual.transfer_mode == TransferMode.LOCAL_FILESYSTEM
        assert actual.s3 is None

    def test_local_filesystem_file_needs_no_s3_block(self, tmp_path: Path) -> None:
        file = write_config(tmp_path, {"data-transfer-mode": "local-filesystem"})

        actual = parse_startup_config(file, mode_from_env=None, env=empty_env())

        assert actual.transfer_mode == TransferMode.LOCAL_FILESYSTEM
        assert actual.s3 is None

    def test_parse_s3_mode(self, tmp_path: Path) -> None:
        file = write_config(
            tmp_path, {"data-transfer-mode": "s3", "s3": dict(S3_BLOCK)}
        )

        actual = parse_startup_config(file, mode_from_env=None, env=empty_env())

        assert actual.transfer_mode == TransferMode.S3
        assert actual.s3 is not None
        assert actual.s3.bucket == "otcloud"
        assert actual.s3.key_prefix == "6-1145/site/OTCamera19/"
        assert actual.s3.max_load_duration == timedelta(hours=10)

    def test_env_overrides_file_transfer_mode(self, tmp_path: Path) -> None:
        """DATA_TRANSFER_MODE wins over the file, as S3_* do for the s3 block.

        # Requirement OP#10256
        """
        file = write_config(
            tmp_path,
            {"data-transfer-mode": "local-filesystem", "s3": dict(S3_BLOCK)},
        )

        actual = parse_startup_config(file, mode_from_env="s3", env=empty_env())

        assert actual.transfer_mode == TransferMode.S3
        assert actual.s3 is not None

    def test_unknown_transfer_mode_is_rejected(self, tmp_path: Path) -> None:
        """OTCloud supports ftp; OTAnalytics does not, and says so.

        # Requirement OP#10256
        """
        file = write_config(tmp_path, {"data-transfer-mode": "ftp"})

        with pytest.raises(InvalidTransferModeError, match="local-filesystem"):
            parse_startup_config(file, mode_from_env=None, env=empty_env())

    def test_s3_settings_may_come_entirely_from_env(self) -> None:
        """A deployment can configure S3 without a config file at all.

        # Requirement OP#10256
        """
        env = empty_env()
        env.access_key = "env-access"
        env.secret_key = "env-secret"  # gitleaks:allow
        env.bucket = "env-bucket"
        env.key_prefix = "env/prefix/"
        env.user_source = "/env/source"

        actual = parse_startup_config(None, mode_from_env="s3", env=env)

        assert actual.transfer_mode == TransferMode.S3
        assert actual.s3 is not None
        assert actual.s3.bucket == "env-bucket"

    def test_s3_mode_without_any_settings_reports_all_missing(self) -> None:
        with pytest.raises(MissingS3ConfigError) as excinfo:
            parse_startup_config(None, mode_from_env="s3", env=empty_env())

        assert excinfo.value.missing == [
            "access-key",
            "secret-key",
            "bucket",
            "key-prefix",
            "user-source",
        ]

    def test_missing_file_is_reported(self, tmp_path: Path) -> None:
        with pytest.raises(StartupConfigError, match="does not exist"):
            parse_startup_config(
                tmp_path / "absent.yaml", mode_from_env=None, env=empty_env()
            )

    def test_empty_file_defaults_to_local_filesystem(self, tmp_path: Path) -> None:
        file = tmp_path / "startup.yaml"
        file.write_text("")

        actual = parse_startup_config(file, mode_from_env=None, env=empty_env())

        assert actual.transfer_mode == TransferMode.LOCAL_FILESYSTEM


class TestParseTransferMode:
    """Reading the mode must not require the S3 settings to be parseable."""

    def test_reads_mode_without_touching_s3_settings(self, tmp_path: Path) -> None:
        """S3 mode with no credentials at all still yields the mode.

        This is what lets the front-end check run first.

        # Requirement OP#10256
        """
        file = write_config(tmp_path, {"data-transfer-mode": "s3"})

        assert parse_transfer_mode(file, mode_from_env=None) == TransferMode.S3

    def test_defaults_to_local_filesystem(self) -> None:
        assert (
            parse_transfer_mode(None, mode_from_env=None)
            == TransferMode.LOCAL_FILESYSTEM
        )

    def test_env_overrides_file(self, tmp_path: Path) -> None:
        file = write_config(tmp_path, {"data-transfer-mode": "local-filesystem"})

        assert parse_transfer_mode(file, mode_from_env="s3") == TransferMode.S3

    def test_unknown_mode_is_rejected(self) -> None:
        with pytest.raises(InvalidTransferModeError):
            parse_transfer_mode(None, mode_from_env="ftp")
