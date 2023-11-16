from unittest.mock import MagicMock, Mock

import pytest
from pandas import DataFrame
from pygeos import Geometry, linestrings

from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import LineSection, Section, SectionId
from OTAnalytics.domain.track import (
    IntersectionPoint,
    Track,
    TrackDataset,
    TrackGeometryDataset,
    TrackId,
)
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    BASE_GEOMETRY,
    GEOMETRY,
    PROJECTION,
    TRACK_ID,
    PygeosTrackGeometryDataset,
)
from tests.conftest import TrackBuilder


def create_pygeos_track(track: Track) -> Geometry:
    return linestrings([(detection.x, detection.y) for detection in track.detections])


def create_track_dataset(tracks: list[Track]) -> TrackDataset:
    dataset = MagicMock()
    dataset.__iter__.return_value = iter(tracks)
    dataset.__len__.return_value = len(tracks)
    return dataset


@pytest.fixture
def first_track() -> Track:
    track_builder = TrackBuilder()
    track_builder.add_track_id("1")
    track_builder.add_xy_bbox(1, 1)
    track_builder.add_frame(1)
    track_builder.add_second(1)
    track_builder.append_detection()

    track_builder.add_xy_bbox(2, 1)
    track_builder.add_frame(2)
    track_builder.add_second(2)
    track_builder.append_detection()

    track_builder.add_xy_bbox(3, 1)
    track_builder.add_frame(3)
    track_builder.add_second(3)
    track_builder.append_detection()

    track_builder.add_xy_bbox(4, 1)
    track_builder.add_frame(4)
    track_builder.add_second(4)
    track_builder.append_detection()

    track_builder.add_xy_bbox(5, 1)
    track_builder.add_frame(5)
    track_builder.add_second(5)
    track_builder.append_detection()

    return track_builder.build_track()


@pytest.fixture
def second_track() -> Track:
    track_builder = TrackBuilder()
    track_builder.add_track_id("2")
    track_builder.add_xy_bbox(1, 1.5)
    track_builder.add_frame(1)
    track_builder.add_second(1)
    track_builder.append_detection()

    track_builder.add_xy_bbox(2, 1.5)
    track_builder.add_frame(2)
    track_builder.add_second(2)
    track_builder.append_detection()

    track_builder.add_xy_bbox(3, 1.5)
    track_builder.add_frame(3)
    track_builder.add_second(3)
    track_builder.append_detection()

    track_builder.add_xy_bbox(4, 1.5)
    track_builder.add_frame(4)
    track_builder.add_second(4)
    track_builder.append_detection()

    track_builder.add_xy_bbox(5, 1.5)
    track_builder.add_frame(5)
    track_builder.add_second(5)
    track_builder.append_detection()

    return track_builder.build_track()


@pytest.fixture
def not_intersecting_track() -> Track:
    track_builder = TrackBuilder()
    track_builder.add_track_id("3")
    track_builder.add_xy_bbox(1, 10)
    track_builder.add_frame(1)
    track_builder.add_second(1)
    track_builder.append_detection()

    track_builder.add_xy_bbox(2, 10)
    track_builder.add_frame(2)
    track_builder.add_second(2)
    track_builder.append_detection()

    track_builder.add_xy_bbox(3, 10)
    track_builder.add_frame(3)
    track_builder.add_second(3)
    track_builder.append_detection()

    track_builder.add_xy_bbox(4, 10)
    track_builder.add_frame(4)
    track_builder.add_second(4)
    track_builder.append_detection()

    track_builder.add_xy_bbox(5, 10)
    track_builder.add_frame(5)
    track_builder.add_second(5)
    track_builder.append_detection()

    return track_builder.build_track()


@pytest.fixture
def not_intersecting_section() -> Section:
    name = "first"
    coordinates = [Coordinate(0, 0), Coordinate(0, 2)]
    return LineSection(
        SectionId(name),
        name,
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
        {},
        coordinates,
    )


@pytest.fixture
def first_section() -> Section:
    name = "first"
    coordinates = [Coordinate(1.5, 0), Coordinate(1.5, 2)]
    return LineSection(
        SectionId(name),
        name,
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
        {},
        coordinates,
    )


@pytest.fixture
def second_section() -> Section:
    name = "second"
    coordinates = [Coordinate(2.5, 0), Coordinate(2.5, 2)]
    return LineSection(
        SectionId(name),
        name,
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
        {},
        coordinates,
    )


@pytest.fixture
def third_section() -> Section:
    name = "third"
    coordinates = [Coordinate(3.5, 0), Coordinate(3.5, 2)]
    return LineSection(
        SectionId(name),
        name,
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
        {},
        coordinates,
    )


def assert_track_geometry_dataset_equals(
    to_compare: TrackGeometryDataset, other: TrackGeometryDataset
) -> None:
    assert isinstance(to_compare, PygeosTrackGeometryDataset)
    assert isinstance(other, PygeosTrackGeometryDataset)
    assert to_compare._dataset.keys() == other._dataset.keys()  # noqa

    for offset, track_geom in to_compare._dataset.items():  # noqa
        assert track_geom.equals(other._dataset[offset])  # noqa


class TestPygeosTrackGeometryDataset:
    @pytest.fixture
    def simple_track(self) -> Track:
        first_detection = Mock()
        first_detection.x = 1
        first_detection.y = 0
        second_detection = Mock()
        second_detection.x = 2
        second_detection.y = 0
        simple_track = Mock()
        simple_track.id = TrackId("1")
        simple_track.detections = [first_detection, second_detection]
        return simple_track

    def test_from_track_dataset(self, simple_track: Track) -> None:
        track_dataset = create_track_dataset([simple_track])
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        assert isinstance(geometry_dataset, PygeosTrackGeometryDataset)
        expected = PygeosTrackGeometryDataset(
            {
                BASE_GEOMETRY: DataFrame.from_records(
                    [
                        (
                            simple_track.id.id,
                            create_pygeos_track(simple_track),
                            [0.0, 1.0],
                        ),
                    ],
                    columns=[TRACK_ID, GEOMETRY, PROJECTION],
                )
            }
        )
        assert_track_geometry_dataset_equals(geometry_dataset, expected)

    @pytest.mark.skip
    def test_add_all(self, first_track: Track, second_track: Track) -> None:
        track_dataset = create_track_dataset([first_track, second_track])
        geometry_dataset = PygeosTrackGeometryDataset({})
        geometry_dataset.add_all(track_dataset)

        expected = PygeosTrackGeometryDataset(
            {
                BASE_GEOMETRY: DataFrame.from_records(
                    [
                        (
                            first_track.id.id,
                            create_pygeos_track(first_track),
                            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
                        ),
                        (
                            second_track.id.id,
                            create_pygeos_track(second_track),
                            [0.0, 1.0, 2.0, 3.0, 4.0, 5.0],
                        ),
                    ]
                )
            }
        )
        assert_track_geometry_dataset_equals(geometry_dataset, expected)

    def test_intersection_points(
        self,
        not_intersecting_track: Track,
        first_track: Track,
        second_track: Track,
        not_intersecting_section: Section,
        first_section: Section,
        second_section: Section,
        third_section: Section,
    ) -> None:
        sections = [
            not_intersecting_section,
            first_section,
            second_section,
            third_section,
        ]
        track_dataset = create_track_dataset(
            [not_intersecting_track, first_track, second_track]
        )
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        result = geometry_dataset.intersection_points(list(sections))
        assert result == {
            first_track.id: [
                (first_section.id, IntersectionPoint(1)),
                (second_section.id, IntersectionPoint(2)),
                (third_section.id, IntersectionPoint(3)),
            ],
            second_track.id: [
                (first_section.id, IntersectionPoint(1)),
                (second_section.id, IntersectionPoint(2)),
                (third_section.id, IntersectionPoint(3)),
            ],
        }

    def test_intersecting_tracks(
        self,
        not_intersecting_track: Track,
        first_track: Track,
        second_track: Track,
        not_intersecting_section: Section,
        first_section: Section,
        second_section: Section,
        third_section: Section,
    ) -> None:
        sections = [
            not_intersecting_section,
            first_section,
            second_section,
            third_section,
        ]
        track_dataset = create_track_dataset(
            [not_intersecting_track, first_track, second_track]
        )
        geometry_dataset = PygeosTrackGeometryDataset.from_track_dataset(track_dataset)
        result = geometry_dataset.intersecting_tracks(list(sections))
        assert result == {first_track.id, second_track.id}
