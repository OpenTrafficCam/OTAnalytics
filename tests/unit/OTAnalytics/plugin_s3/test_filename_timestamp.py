"""Tests for reading the recording start time out of an object's filename."""

from datetime import datetime, timezone

import pytest

from OTAnalytics.plugin_s3.filename_timestamp import (
    NoTimestampInFilename,
    parse_timestamp,
)


class TestParseTimestamp:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    @pytest.mark.parametrize(
        "key, expected",
        [
            pytest.param(
                "OTCamera19_FR20_2023-05-24_06-00-00.ottrk",
                datetime(2023, 5, 24, 6, 0, 0, tzinfo=timezone.utc),
                id="ottrk",
            ),
            pytest.param(
                "prefix/sub/OTCamera19_FR20_2023-05-24_06-15-00.mp4",
                datetime(2023, 5, 24, 6, 15, 0, tzinfo=timezone.utc),
                id="key_with_prefix",
            ),
            pytest.param(
                "cam_with_many_underscores_2024-01-02_23-59-59.ottrk",
                datetime(2024, 1, 2, 23, 59, 59, tzinfo=timezone.utc),
                id="extra_underscores",
            ),
            pytest.param(
                "OTCamera19.FR20.extra.dots_2023-05-24_06-00-00.mp4",
                datetime(2023, 5, 24, 6, 0, 0, tzinfo=timezone.utc),
                id="extra_dots",
            ),
        ],
    )
    def test_reads_the_timestamp_as_utc(self, key: str, expected: datetime) -> None:
        """Filename digits are UTC, matching OTVision's own convention."""
        assert parse_timestamp(key) == expected

    @pytest.mark.parametrize(
        "key",
        [
            pytest.param("OTCamera19_FR20.ottrk", id="no_timestamp"),
            pytest.param("OTCamera19_2023-05-24.ottrk", id="date_without_time"),
            pytest.param("", id="empty"),
        ],
    )
    def test_rejects_a_name_without_a_timestamp(self, key: str) -> None:
        with pytest.raises(NoTimestampInFilename):
            parse_timestamp(key)
