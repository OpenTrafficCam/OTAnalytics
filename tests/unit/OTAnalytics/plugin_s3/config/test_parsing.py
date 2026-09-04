"""Tests for building the S3 configuration from environment variables."""

from datetime import timedelta

import pytest

from OTAnalytics.plugin_s3.config.env_vars import S3Env
from OTAnalytics.plugin_s3.config.parsing import (
    InvalidDurationError,
    MissingS3ConfigError,
    parse_duration,
    parse_s3_config,
)


def env(**overrides: str | None) -> S3Env:
    """An S3Env with nothing set, then the given overrides applied."""
    values: dict[str, str | None] = {
        "endpoint_url": None,
        "access_key": None,
        "secret_key": None,
        "bucket": None,
        "region": None,
        "key_prefix": None,
        "user_source": None,
        "max_load_duration": None,
        "download_concurrency": None,
    }
    values.update(overrides)
    return S3Env(**values)


def complete_env(**overrides: str | None) -> S3Env:
    """An S3Env with every required variable set, then the overrides applied."""
    required: dict[str, str | None] = {
        "access_key": "minioadmin",
        "secret_key": "minioadmin",  # gitleaks:allow
        "bucket": "otcloud",
        "key_prefix": "6-1145/site/OTCamera19/",
        "user_source": "/data/otanalytics-source",
    }
    required.update(overrides)
    return env(**required)


class TestParseDuration:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("10h", timedelta(hours=10)),
            ("45m", timedelta(minutes=45)),
            ("90s", timedelta(seconds=90)),
            ("1h", timedelta(hours=1)),
        ],
    )
    def test_parse_supported_units(self, value: str, expected: timedelta) -> None:
        assert parse_duration(value) == expected

    @pytest.mark.parametrize("value", ["10", "10d", "h", "", "-1h", "1.5h", "ten h"])
    def test_reject_malformed_duration(self, value: str) -> None:
        """A unit suffix is required so `10` cannot silently mean seconds.

        # Requirement OP#10256
        """
        with pytest.raises(InvalidDurationError):
            parse_duration(value)


class TestParseS3Config:
    def test_parse_every_variable(self) -> None:
        actual = parse_s3_config(
            complete_env(
                endpoint_url="http://localhost:9000",
                region="us-east-1",
                max_load_duration="2h",
                download_concurrency="16",
            )
        )

        assert actual.endpoint_url == "http://localhost:9000"
        assert actual.access_key == "minioadmin"
        assert actual.bucket == "otcloud"
        assert actual.region == "us-east-1"
        assert actual.key_prefix == "6-1145/site/OTCamera19/"
        assert actual.user_source == "/data/otanalytics-source"
        assert actual.max_load_duration == timedelta(hours=2)
        assert actual.download_concurrency == 16

    def test_optional_variables_default(self) -> None:
        """Endpoint and region are optional; the policy settings have defaults.

        # Requirement OP#10256
        """
        actual = parse_s3_config(complete_env())

        assert actual.endpoint_url is None
        assert actual.region is None
        assert actual.max_load_duration == timedelta(hours=10)
        assert actual.download_concurrency == 8

    def test_empty_key_prefix_is_kept(self) -> None:
        """`S3_KEY_PREFIX=""` means the bucket root, not "unset".

        # Requirement OP#10256
        """
        actual = parse_s3_config(complete_env(key_prefix=""))

        assert actual.key_prefix == ""

    def test_malformed_duration_is_rejected(self) -> None:
        with pytest.raises(InvalidDurationError):
            parse_s3_config(complete_env(max_load_duration="10"))


class TestMissingRequiredVariables:
    def test_report_every_missing_variable_at_once(self) -> None:
        """All missing variables are named, not just the first one found.

        An operator fixing one variable per restart is a bad loop.

        # Requirement OP#10256
        """
        with pytest.raises(MissingS3ConfigError) as excinfo:
            parse_s3_config(env(bucket="otcloud"))

        assert excinfo.value.missing == [
            "S3_ACCESS_KEY",
            "S3_SECRET_KEY",
            "S3_KEY_PREFIX",
            "S3_USER_SOURCE",
        ]

    def test_only_absent_variables_are_reported(self) -> None:
        with pytest.raises(MissingS3ConfigError) as excinfo:
            parse_s3_config(env(bucket="otcloud", access_key="a", user_source="/src"))

        assert excinfo.value.missing == ["S3_SECRET_KEY", "S3_KEY_PREFIX"]

    def test_message_names_the_environment_variables(self) -> None:
        with pytest.raises(MissingS3ConfigError, match="S3_ACCESS_KEY"):
            parse_s3_config(env())


class TestS3EnvFromEnvironment:
    def test_reads_environment_variables(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("S3_BUCKET", "from-env")
        monkeypatch.setenv("S3_ACCESS_KEY", "key-from-env")
        monkeypatch.setenv("S3_MAX_LOAD_DURATION", "3h")

        actual = S3Env()

        assert actual.bucket == "from-env"
        assert actual.access_key == "key-from-env"
        assert actual.max_load_duration == "3h"

    def test_unset_variables_are_none(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for name in (
            "S3_ENDPOINT_URL",
            "S3_ACCESS_KEY",
            "S3_SECRET_KEY",
            "S3_BUCKET",
            "S3_REGION",
            "S3_KEY_PREFIX",
            "S3_USER_SOURCE",
            "S3_MAX_LOAD_DURATION",
            "S3_DOWNLOAD_CONCURRENCY",
        ):
            monkeypatch.delenv(name, raising=False)

        actual = S3Env()

        assert actual.bucket is None
        assert actual.max_load_duration is None
