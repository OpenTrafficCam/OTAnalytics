import pytest

from OTAnalytics.domain.track import Track, TrackId
from tests.utils.builders.track_builder import create_track
from tests.utils.builders.track_dataset_provider import TrackDatasetProvider

FIRST_TRACK_ID = TrackId("1")
UNCUT_TRACK_ID = TrackId("uncut-2")
FIRST_TRACK_PART_1_COORD = [(1, 1), (2, 1)]
FIRST_TRACK_PART_2_COORD = [(3, 1), (4, 1)]


@pytest.fixture
def track_dataset_provider() -> TrackDatasetProvider:
    return TrackDatasetProvider()


@pytest.fixture
def first_track_part_1() -> Track:
    return create_track(
        track_id="1_1",
        original_id=FIRST_TRACK_ID.id,
        coord=FIRST_TRACK_PART_1_COORD,
        start_second=1,
    )


@pytest.fixture
def first_track_part_2() -> Track:
    return create_track(
        track_id="1_2",
        original_id=FIRST_TRACK_ID.id,
        coord=FIRST_TRACK_PART_2_COORD,
        start_second=3,
    )


@pytest.fixture
def uncut_track() -> Track:
    return create_track(
        track_id=UNCUT_TRACK_ID.id,
        coord=[(1, 2), (2, 2)],
        start_second=1,
    )


@pytest.fixture
def expected_first_track(first_track_part_1: Track, first_track_part_2: Track) -> Track:
    return create_track(
        track_id=FIRST_TRACK_ID.id,
        coord=FIRST_TRACK_PART_1_COORD + FIRST_TRACK_PART_2_COORD,
        start_second=1,
    )
