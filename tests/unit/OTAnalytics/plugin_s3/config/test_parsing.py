"""Tests for parsing the `s3` block of the startup configuration."""

from datetime import timedelta

import pytest

from OTAnalytics.plugin_s3.config.env_vars import S3Env
from OTAnalytics.plugin_s3.config.parsing import (
    InvalidDurationError,
    MissingS3ConfigError,
    parse_duration,
    parse_s3_config,
)

FULL_S3_BLOCK = {
    "endpoint-url": "http://localhost:9000",
    "access-key": "minioadmin",
    "secret-key": "minioadmin",  # gitleaks:allow
    "bucket": "otcloud",
    "region": "us-east-1",
    "key-prefix": "6-1145/site/OTCamera19/",
    "user-source": "/data/otanalytics-source",
    "max-load-duration": "10h",
    "download-concurrency": 8,
}

MINIMAL_S3_BLOCK = {
    "access-key": "minioadmin",
    "secret-key": "minioadmin",  # gitleaks:allow
    "bucket": "otcloud",
    "key-prefix": "6-1145/site/OTCamera19/",
    "user-source": "/data/otanalytics-source",
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
    def test_parse_full_block(self) -> None:
        actual = parse_s3_config(FULL_S3_BLOCK, empty_env())

        assert actual.endpoint_url == "http://localhost:9000"
        assert actual.access_key == "minioadmin"
        assert actual.bucket == "otcloud"
        assert actual.region == "us-east-1"
        assert actual.key_prefix == "6-1145/site/OTCamera19/"
        assert actual.user_source == "/data/otanalytics-source"
        assert actual.max_load_duration == timedelta(hours=10)
        assert actual.download_concurrency == 8

    def test_optional_fields_default(self) -> None:
        """endpoint-url and region are optional; the two policy fields default.

        # Requirement OP#10256
        """
        actual = parse_s3_config(MINIMAL_S3_BLOCK, empty_env())

        assert actual.endpoint_url is None
        assert actual.region is None
        assert actual.max_load_duration == timedelta(hours=10)
        assert actual.download_concurrency == 8

    def test_env_overrides_file_values(self) -> None:
        """Environment wins, so secrets need not live in a file at all.

        # Requirement OP#10256
        """
        env = S3Env(
            endpoint_url="https://minio.internal:9000",
            access_key="env-access",
            secret_key="env-secret",  # gitleaks:allow
            bucket="env-bucket",
            region="eu-central-1",
            key_prefix="env/prefix/",
            user_source="/env/source",
            max_load_duration="2h",
            download_concurrency="16",
        )

        actual = parse_s3_config(FULL_S3_BLOCK, env)

        assert actual.endpoint_url == "https://minio.internal:9000"
        assert actual.access_key == "env-access"
        assert actual.secret_key == "env-secret"  # gitleaks:allow
        assert actual.bucket == "env-bucket"
        assert actual.region == "eu-central-1"
        assert actual.key_prefix == "env/prefix/"
        assert actual.user_source == "/env/source"
        assert actual.max_load_duration == timedelta(hours=2)
        assert actual.download_concurrency == 16

    def test_env_supplies_values_absent_from_file(self) -> None:
        env = empty_env()
        env.access_key = "env-access"
        env.secret_key = "env-secret"  # gitleaks:allow

        actual = parse_s3_config(
            {
                "bucket": "otcloud",
                "key-prefix": "6-1145/",
                "user-source": "/data/source",
            },
            env,
        )

        assert actual.access_key == "env-access"
        assert actual.secret_key == "env-secret"  # gitleaks:allow


class TestMissingRequiredFields:
    def test_report_every_missing_field_at_once(self) -> None:
        """All missing fields are named, not just the first one found.

        An operator fixing one variable per restart is a bad loop.

        # Requirement OP#10256
        """
        with pytest.raises(MissingS3ConfigError) as excinfo:
            parse_s3_config({"bucket": "otcloud"}, empty_env())

        assert excinfo.value.missing == [
            "access-key",
            "secret-key",
            "key-prefix",
            "user-source",
        ]

    def test_field_supplied_by_env_is_not_reported_missing(self) -> None:
        env = empty_env()
        env.access_key = "env-access"
        env.user_source = "/env/source"

        with pytest.raises(MissingS3ConfigError) as excinfo:
            parse_s3_config({"bucket": "otcloud"}, env)

        assert excinfo.value.missing == ["secret-key", "key-prefix"]

    def test_message_names_the_missing_fields(self) -> None:
        with pytest.raises(MissingS3ConfigError, match="access-key"):
            parse_s3_config({"bucket": "otcloud"}, empty_env())


class TestS3EnvFromEnvironment:
    def test_reads_environment_variables(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("S3_BUCKET", "from-env")
        monkeypatch.setenv("S3_ACCESS_KEY", "key-from-env")
        monkeypatch.setenv("S3_MAX_LOAD_DURATION", "3h")

        env = S3Env()

        assert env.bucket == "from-env"
        assert env.access_key == "key-from-env"
        assert env.max_load_duration == "3h"

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

        env = S3Env()

        assert env.bucket is None
        assert env.max_load_duration is None


class TestEmptyEnvValues:
    def test_empty_env_value_is_an_override_not_a_fallback(self) -> None:
        """`S3_KEY_PREFIX=""` means the bucket root, not "use the file".

        Truthiness-based precedence would silently read the file value here.

        # Requirement OP#10256
        """
        env = empty_env()
        env.key_prefix = ""

        actual = parse_s3_config(dict(FULL_S3_BLOCK), env)

        assert actual.key_prefix == ""
