"""Tests for choosing which S3 objects fall inside the selected Load Window."""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from OTAnalytics.domain.load_window import LoadWindow
from OTAnalytics.plugin_s3.select_objects import select_in_window

START = datetime(2023, 5, 24, 6, 0, tzinfo=timezone.utc)

AT_0545 = "cam/OTCamera19_2023-05-24_05-45-00.ottrk"
AT_0600 = "cam/OTCamera19_2023-05-24_06-00-00.ottrk"
AT_0615 = "cam/OTCamera19_2023-05-24_06-15-00.ottrk"
AT_0700 = "cam/OTCamera19_2023-05-24_07-00-00.ottrk"
AT_0715 = "cam/OTCamera19_2023-05-24_07-15-00.ottrk"
VIDEO_0600 = "cam/OTCamera19_2023-05-24_06-00-00.mp4"

ALL_KEYS = [AT_0715, AT_0545, AT_0700, AT_0600, AT_0615, VIDEO_0600]


@dataclass
class Given:
    keys: list[str]
    window: LoadWindow


def create_given(hours: float = 1, keys: list[str] | None = None) -> Given:
    return Given(
        keys=ALL_KEYS if keys is None else keys,
        window=LoadWindow(start=START, end=START + timedelta(hours=hours)),
    )


class TestSelectInWindow:
    """#Requirement https://openproject.platomo.de/wp/10283"""

    def test_keeps_only_the_requested_suffixes(self) -> None:
        given = create_given()

        selected = select_in_window(given.keys, given.window, {".ottrk"})

        assert VIDEO_0600 not in selected

    def test_includes_both_boundaries(self) -> None:
        given = create_given(hours=1)

        selected = select_in_window(given.keys, given.window, {".ottrk"})

        assert AT_0600 in selected
        assert AT_0700 in selected

    def test_drops_a_chunk_starting_before_the_window(self) -> None:
        """Strict start-in-range: a 05:45 chunk is not loaded for a 06:00 start."""
        given = create_given(hours=1)

        selected = select_in_window(given.keys, given.window, {".ottrk"})

        assert AT_0545 not in selected

    def test_drops_a_chunk_starting_after_the_window(self) -> None:
        given = create_given(hours=1)

        selected = select_in_window(given.keys, given.window, {".ottrk"})

        assert AT_0715 not in selected

    def test_returns_them_in_recording_order(self) -> None:
        given = create_given(hours=1)

        selected = select_in_window(given.keys, given.window, {".ottrk"})

        assert selected == [AT_0600, AT_0615, AT_0700]

    def test_ignores_objects_without_a_timestamp(self) -> None:
        """A bucket may hold anything; unrelated objects must not break a load."""
        given = create_given(hours=1, keys=[AT_0600, "cam/notes.ottrk", "cam/"])

        selected = select_in_window(given.keys, given.window, {".ottrk"})

        assert selected == [AT_0600]

    def test_matches_suffixes_regardless_of_case(self) -> None:
        given = create_given(hours=1, keys=["cam/OTCamera19_2023-05-24_06-00-00.OTTRK"])

        selected = select_in_window(given.keys, given.window, {".ottrk"})

        assert selected == ["cam/OTCamera19_2023-05-24_06-00-00.OTTRK"]
