from typing import Iterable
from unittest.mock import Mock

import pytest

from OTAnalytics.domain.geometry import Coordinate
from OTAnalytics.domain.section import LineSection, SectionId
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset import (
    TRACK_GEOMETRY_FACTORY,
    TrackDataset,
    TrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    CLASS_BICYCLIST,
    CLASS_CAR,
    CLASS_CARGOBIKE,
    CLASS_PEDESTRIAN,
    CLASS_TRUCK,
)
from tests.conftest import assert_equal_track_properties, create_track


def create_mock_geometry_dataset(
    get_for_side_effect: list[Mock] | None = None,
) -> tuple[Mock, Mock]:
    geometry_dataset = Mock(spec=TrackGeometryDataset)
    updated_geometry_dataset = Mock()
    geometry_dataset.add_all.return_value = updated_geometry_dataset
    geometry_dataset.remove.return_value = updated_geometry_dataset
    if get_for_side_effect is not None:
        geometry_dataset.get_for.side_effect = get_for_side_effect
    return geometry_dataset, updated_geometry_dataset


def assert_track_geometry_dataset_add_all_called_correctly(
    called_method: Mock, expected_arg: Iterable[Track]
) -> None:
    for actual_track, expected_track in zip(
        called_method.call_args_list[0][0][0], expected_arg
    ):
        assert_equal_track_properties(actual_track, expected_track)


def assert_track_dataset_has_tracks(dataset: TrackDataset, tracks: list[Track]) -> None:
    assert len(dataset) == len(tracks)
    for expected in tracks:
        actual = dataset.get_for(expected.id)
        assert actual
        assert_equal_track_properties(actual, expected)


@pytest.fixture
def track_geometry_factory() -> TRACK_GEOMETRY_FACTORY:
    return PygeosTrackGeometryDataset.from_track_dataset


@pytest.fixture
def first_track() -> Track:
    return create_track("1", [(1, 1), (2, 2)], 1, CLASS_CAR)


@pytest.fixture
def first_track_continuing() -> Track:
    return create_track("1", [(3, 3), (4, 4), (5, 5)], 3, CLASS_TRUCK)


@pytest.fixture
def second_track() -> Track:
    return create_track("2", [(1, 1), (2, 2), (3, 3)], 1, CLASS_PEDESTRIAN)


@pytest.fixture
def bicycle_track() -> Track:
    return create_track("3", [(1, 1), (2, 2), (3, 3)], 4, CLASS_BICYCLIST)


@pytest.fixture
def cargo_bike_track() -> Track:
    return create_track("4", [(1, 1), (2, 2), (3, 3)], 4, CLASS_CARGOBIKE)


@pytest.fixture
def tracks(
    first_track: Track,
    second_track: Track,
    bicycle_track: Track,
    cargo_bike_track: Track,
) -> list[Track]:
    return [first_track, second_track, bicycle_track, cargo_bike_track]


@pytest.fixture
def cutting_section_test_case() -> (
    tuple[LineSection, list[Track], list[Track], set[TrackId]]
):
    first_track = create_track(
        "1",
        [(1, 1), (2, 1), (3, 1), (4, 1), (4, 2), (3, 2), (2, 2), (1, 2)],
        start_second=1,
    )
    expected_first_track_1 = create_track(
        "1_0",
        [
            (1, 1),
            (2, 1),
        ],
        1,
    )
    expected_first_track_2 = create_track("1_1", [(3, 1), (4, 1), (4, 2), (3, 2)], 3)
    expected_first_track_3 = create_track("1_2", [(2, 2), (1, 2)], 7)

    second_track = create_track("2", [(1, 1), (2, 1), (3, 1)], 1)
    expected_second_track_1 = create_track("2_0", [(1, 1), (2, 1)], 1)
    expected_second_track_2 = create_track("2_1", [(3, 1)], 3)

    third_track = create_track("3", [(10, 10), (20, 10)], 10)

    _id = "#cut_1"
    cutting_section = LineSection(
        SectionId(_id), _id, {}, {}, [Coordinate(2.5, 0), Coordinate(2.5, 3)]
    )

    expected_original_track_ids = {first_track.id, second_track.id}

    return (
        cutting_section,
        [first_track, second_track, third_track],
        [
            expected_first_track_1,
            expected_first_track_2,
            expected_first_track_3,
            expected_second_track_1,
            expected_second_track_2,
        ],
        expected_original_track_ids,
    )
