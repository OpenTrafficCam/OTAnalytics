from typing import Iterable
from unittest.mock import Mock

import pytest

from OTAnalytics.domain.geometry import Coordinate
from OTAnalytics.domain.section import LineSection, SectionId
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset import (
    TRACK_GEOMETRY_FACTORY,
    TrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)
from tests.conftest import TrackBuilder, assert_equal_track_properties, create_track


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


@pytest.fixture
def track_geometry_factory() -> TRACK_GEOMETRY_FACTORY:
    return PygeosTrackGeometryDataset.from_track_dataset


@pytest.fixture
def first_track() -> Track:
    track_builder = TrackBuilder()
    _class = "car"

    track_builder.add_track_id("1")
    track_builder.add_track_class(_class)
    track_builder.add_second(1)
    track_builder.add_frame(1)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    track_builder.add_track_class(_class)
    track_builder.add_second(2)
    track_builder.add_frame(2)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    return track_builder.build_track()


@pytest.fixture
def first_track_continuing() -> Track:
    track_builder = TrackBuilder()
    _class = "truck"
    track_builder.add_track_id("1")
    track_builder.add_track_class(_class)
    track_builder.add_second(3)
    track_builder.add_frame(3)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    track_builder.add_track_class(_class)
    track_builder.add_second(4)
    track_builder.add_frame(4)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    track_builder.add_track_class(_class)
    track_builder.add_second(5)
    track_builder.add_frame(5)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    return track_builder.build_track()


@pytest.fixture
def second_track() -> Track:
    track_builder = TrackBuilder()
    _class = "pedestrian"
    track_builder.add_track_id("2")
    track_builder.add_track_class(_class)
    track_builder.add_second(1)
    track_builder.add_frame(1)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    track_builder.add_track_class(_class)
    track_builder.add_second(2)
    track_builder.add_frame(2)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    track_builder.add_track_class(_class)
    track_builder.add_second(3)
    track_builder.add_frame(3)
    track_builder.add_detection_class(_class)
    track_builder.append_detection()

    return track_builder.build_track()


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
