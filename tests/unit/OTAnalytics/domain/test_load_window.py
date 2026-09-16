"""Tests for the Load Window a user selects before loading from S3."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest

from OTAnalytics.domain.load_window import LoadWindow

START = datetime(2026, 8, 27, 6, 0, tzinfo=timezone.utc)
TEN_HOURS = timedelta(hours=10)


@dataclass
class Given:
    start: datetime
    end: datetime
    maximum: timedelta


def create_given(hours: float = 2, maximum: timedelta = TEN_HOURS) -> Given:
    return Given(start=START, end=START + timedelta(hours=hours), maximum=maximum)


def create_target(given: Given) -> LoadWindow:
    return LoadWindow(start=given.start, end=given.end)


class TestLoadWindow:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    def test_knows_its_duration(self) -> None:
        given = create_given(hours=2)
        target = create_target(given)

        assert target.duration == timedelta(hours=2)

    def test_a_window_within_the_maximum_is_left_alone(self) -> None:
        given = create_given(hours=2)
        target = create_target(given)

        clamped = target.clamp(given.maximum)

        assert clamped == target
        assert clamped.was_clamped is False

    def test_a_window_exactly_at_the_maximum_is_left_alone(self) -> None:
        given = create_given(hours=10)
        target = create_target(given)

        clamped = target.clamp(given.maximum)

        assert clamped.end == given.end
        assert clamped.was_clamped is False

    def test_an_over_long_window_snaps_its_end_to_the_maximum(self) -> None:
        given = create_given(hours=24)
        target = create_target(given)

        clamped = target.clamp(given.maximum)

        assert clamped.start == START
        assert clamped.end == START + TEN_HOURS
        assert clamped.was_clamped is True

    def test_an_end_before_the_start_is_rejected(self) -> None:
        with pytest.raises(ValueError):
            LoadWindow(start=START, end=START - timedelta(minutes=1))

    def test_contains_only_timestamps_within_the_window(self) -> None:
        given = create_given(hours=2)
        target = create_target(given)

        assert target.contains(START) is True
        assert target.contains(START + timedelta(hours=1)) is True
        assert target.contains(given.end) is True
        assert target.contains(START - timedelta(seconds=1)) is False
        assert target.contains(given.end + timedelta(seconds=1)) is False
