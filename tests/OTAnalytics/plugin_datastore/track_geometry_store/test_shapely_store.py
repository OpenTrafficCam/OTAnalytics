from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from unittest.mock import MagicMock, Mock, patch

import pytest
from pandas import DataFrame
from pytest_benchmark.fixture import BenchmarkFixture
from shapely import get_coordinates, line_locate_point, points

from OTAnalytics.application.config import DEFAULT_TRACK_OFFSET
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import Area, LineSection, Section, SectionId
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset.track_dataset import (
    TRACK_GEOMETRY_FACTORY,
    IntersectionPoint,
    TrackDataset,
    TrackGeometryDataset,
)
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_datastore.track_geometry_store.shapely_store import (
    BASE_GEOMETRY,
    COLUMNS,
    GEOMETRY,
    NDIGITS_DISTANCE,
    PROJECTION,
    TRACK_ID,
    ShapelyTrackGeometryDataset,
    create_shapely_track,
    distance_on_track,
)
from OTAnalytics.plugin_datastore.track_store import (
    PandasByMaxConfidence,
    PandasTrackDataset,
)
from OTAnalytics.plugin_parser.otvision_parser import OtFlowParser, OttrkParser
from OTAnalytics.plugin_parser.pandas_parser import PandasDetectionParser
from tests.utils.builders.track_builder import TrackBuilder


def create_track_dataset(tracks: list[Track]) -> TrackDataset:
    dataset = MagicMock()
    dataset.__iter__.return_value = iter(tracks)
    dataset.__len__.return_value = len(tracks)
    return dataset


def create_line_section(
    section_id: str, coordinates: list[tuple[float, float]]
) -> Section:
    section = Mock(spec=LineSection)
    section.get_coordinates.return_value = [
        Coordinate(coord[0], coord[1]) for coord in coordinates
    ]
    section.id = SectionId(section_id)
    return section


def create_geometry_dataset_from(
    tracks: Iterable[Track], offset: RelativeOffsetCoordinate
) -> ShapelyTrackGeometryDataset:
    entries = []
    for track in tracks:
        _id = track.id.id
        geometry = create_shapely_track(track, offset)
        projection = [
            distance_on_track(points(p), geometry) for p in get_coordinates(geometry)
        ]
        entries.append((_id, geometry, projection))
    return ShapelyTrackGeometryDataset(
        offset,
        DataFrame.from_records(
            entries,
            columns=[TRACK_ID, GEOMETRY, PROJECTION],
        ).set_index(TRACK_ID),
    )


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
def first_track_merged(first_track: Track) -> Track:
    track_builder = TrackBuilder()
    track_builder.add_track_id("1")
    track_builder.add_xy_bbox(6, 1)
    track_builder.add_frame(6)
    track_builder.add_second(6)
    track_builder.append_detection()

    track_builder.add_xy_bbox(7, 1)
    track_builder.add_frame(7)
    track_builder.add_second(7)
    track_builder.append_detection()

    track_builder.add_xy_bbox(8, 1)
    track_builder.add_frame(8)
    track_builder.add_second(8)
    track_builder.append_detection()

    track_builder.add_xy_bbox(9, 1)
    track_builder.add_frame(9)
    track_builder.add_second(9)
    track_builder.append_detection()

    track_builder.add_xy_bbox(10, 1)
    track_builder.add_frame(10)
    track_builder.add_second(10)
    track_builder.append_detection()
    track = track_builder.build_track()
    merged_track = Mock()
    merged_track.detections = first_track.detections + track.detections
    merged_track.id = first_track.id
    return merged_track


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
    track_builder.add_track_id("not_intersecting_track")
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
def single_detection_track_dataset(
    track_geometry_factory: TRACK_GEOMETRY_FACTORY,
) -> PandasTrackDataset:
    track_builder = TrackBuilder()
    track_builder.append_detection()
    single_detection_track = track_builder.build_track()
    return PandasTrackDataset.from_list(
        [single_detection_track], track_geometry_factory
    )


@pytest.fixture
def single_detection_track() -> Track:
    detection = Mock()
    detection.x = 1
    detection.y = 1
    detection.w = 1
    detection.h = 1
    track = Mock()
    track.id = TrackId("Single-Detection")
    track.detections = [detection]
    return track


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


@pytest.fixture
def forth_section() -> Section:
    name = "third"
    coordinates = [Coordinate(4.25, 0), Coordinate(4.25, 2)]
    return LineSection(
        SectionId(name),
        name,
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
        {},
        coordinates,
    )


@pytest.fixture
def area_section() -> Section:
    name = "area"
    coordinates = [
        Coordinate(1.5, 0.5),
        Coordinate(3, 0.5),
        Coordinate(3, 2),
        Coordinate(1.5, 2),
        Coordinate(1.5, 0.5),
    ]
    return Area(
        SectionId(name),
        name,
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
        {},
        coordinates,
    )


@pytest.fixture
def not_intersecting_area_section() -> Section:
    name = "not_intersecting_area"
    coordinates = [
        Coordinate(20, 20),
        Coordinate(30, 20),
        Coordinate(30, 30),
        Coordinate(20, 30),
        Coordinate(20, 20),
    ]
    return Area(
        SectionId(name),
        name,
        {EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)},
        {},
        coordinates,
    )


def assert_track_geometry_dataset_equals(
    to_compare: TrackGeometryDataset, other: TrackGeometryDataset
) -> None:
    assert isinstance(to_compare, ShapelyTrackGeometryDataset)
    assert isinstance(other, ShapelyTrackGeometryDataset)
    assert to_compare.offset == other.offset
    assert to_compare._dataset.equals(other._dataset)  # noqa


@dataclass
class ContainedBySectionTestCase:
    tracks: list[Track]
    sections: list[Section]
    expected_result: dict[TrackId, list[tuple[SectionId, list[bool]]]]


@pytest.fixture
def contained_by_section_test_case(
    straight_track: Track, complex_track: Track, closed_track: Track
) -> ContainedBySectionTestCase:
    # Straight track starts outside section
    first_section = create_line_section(
        "1", [(1.5, 0.5), (1.5, 1.5), (2.5, 1.5), (2.5, 0.5), (1.5, 0.5)]
    )
    # Straight track starts inside section
    second_section = create_line_section(
        "2", [(0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)]
    )
    # Straight track is inside section
    third_section = create_line_section(
        "3", [(0.0, 0.0), (0.0, 2.0), (4.0, 2.0), (4.0, 0.0), (0.0, 0.0)]
    )
    # Straight track starts outside stays inside section
    fourth_section = create_line_section(
        "4", [(1.5, 0.5), (1.5, 1.5), (4.0, 1.5), (4.0, 0.5), (1.5, 0.5)]
    )
    # Complex track starts outside section with multiple intersections
    fifth_section = create_line_section(
        "5",
        [(1.5, 0.5), (1.5, 2.5), (2.5, 2.5), (2.5, 0.5), (1.5, 0.5)],
    )
    # Complex track starts inside section with multiple intersections
    sixth_section = create_line_section(
        "6", [(0.5, 0.5), (0.5, 2.5), (1.5, 2.5), (1.5, 0.5), (0.5, 0.5)]
    )
    # Closed track
    seventh_section = create_line_section(
        "7", [(1.5, 0.5), (1.5, 2.0), (2.5, 2.0), (2.5, 0.5), (1.5, 0.5)]
    )
    # Not contained track
    eighth_section = create_line_section(
        "not-contained", [(3.0, 1.0), (3.0, 2.0), (4.0, 2.0), (4.0, 1.0), (3.0, 1.0)]
    )
    expected = {
        straight_track.id: [
            (first_section.id, [False, True, False]),
            (second_section.id, [True, False, False]),
            (third_section.id, [True, True, True]),
            (fourth_section.id, [False, True, True]),
            (fifth_section.id, [False, True, False]),
            (sixth_section.id, [True, False, False]),
            (seventh_section.id, [False, True, False]),
        ],
        complex_track.id: [
            (first_section.id, [False, True, False, False, False, False]),
            (second_section.id, [True, False, False, False, False, False]),
            (third_section.id, [True, True, True, True, False, False]),
            (fourth_section.id, [False, True, False, False, False, False]),
            (fifth_section.id, [False, True, True, False, False, True]),
            (sixth_section.id, [True, False, False, True, True, False]),
            (seventh_section.id, [False, True, True, False, False, False]),
        ],
        closed_track.id: [
            (first_section.id, [False, True, False, False, False]),
            (second_section.id, [True, False, False, False, True]),
            (third_section.id, [True, True, False, False, True]),
            (fourth_section.id, [False, True, False, False, False]),
            (fifth_section.id, [False, True, True, False, False]),
            (sixth_section.id, [True, False, False, True, True]),
            (seventh_section.id, [False, True, False, False, False]),
        ],
    }
    return ContainedBySectionTestCase(
        [straight_track, complex_track, closed_track],
        [
            first_section,
            second_section,
            third_section,
            fourth_section,
            fifth_section,
            sixth_section,
            seventh_section,
            eighth_section,
        ],
        expected,
    )


def test_distance_on_track(first_track: Track) -> None:
    """
    Fix https://openproject.platomo.de/projects/otanalytics/work_packages/6836/activity
    """
    geometry = create_shapely_track(first_track, BASE_GEOMETRY)
    original = [
        line_locate_point(geometry, points(p)) for p in get_coordinates(geometry)
    ]
    rounded = [
        line_locate_point(geometry, points(p)) for p in get_coordinates(geometry)
    ]
    for expected, actual in zip(original, rounded):
        assert abs(actual - expected) <= pow(10, -NDIGITS_DISTANCE)


class TestShapelyTrackGeometryDataset:
    @pytest.fixture
    def simple_track(self) -> Track:
        first_detection = Mock()
        first_detection.x = 1
        first_detection.y = 0
        first_detection.w = 4
        first_detection.h = 4
        second_detection = Mock()
        second_detection.x = 2
        second_detection.y = 0
        second_detection.w = 5
        second_detection.h = 5
        simple_track = Mock()
        simple_track.id = TrackId("1")
        simple_track.detections = [first_detection, second_detection]
        return simple_track

    @pytest.mark.parametrize("offset", [BASE_GEOMETRY, DEFAULT_TRACK_OFFSET])
    def test_from_track_dataset(
        self, simple_track: Track, offset: RelativeOffsetCoordinate
    ) -> None:
        track_dataset = create_track_dataset([simple_track])
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            dataset=track_dataset, offset=offset
        )
        assert isinstance(geometry_dataset, ShapelyTrackGeometryDataset)

        expected = create_geometry_dataset_from([simple_track], offset)
        assert_track_geometry_dataset_equals(geometry_dataset, expected)

    @pytest.mark.parametrize("offset", [BASE_GEOMETRY, DEFAULT_TRACK_OFFSET])
    def test_add_all_on_empty_dataset(
        self, first_track: Track, second_track: Track, offset: RelativeOffsetCoordinate
    ) -> None:
        track_dataset = create_track_dataset([])
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, offset
        )
        result = geometry_dataset.add_all([first_track, second_track])
        expected = create_geometry_dataset_from([first_track, second_track], offset)
        assert_track_geometry_dataset_equals(result, expected)

    @pytest.mark.parametrize("offset", [BASE_GEOMETRY, DEFAULT_TRACK_OFFSET])
    def test_add_all_on_filled_dataset(
        self, first_track: Track, second_track: Track, offset: RelativeOffsetCoordinate
    ) -> None:
        track_dataset = create_track_dataset([first_track])
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, offset
        )
        result = geometry_dataset.add_all([second_track])
        expected = create_geometry_dataset_from([first_track, second_track], offset)
        assert_track_geometry_dataset_equals(result, expected)

    @pytest.mark.parametrize("offset", [BASE_GEOMETRY, DEFAULT_TRACK_OFFSET])
    def test_add_all_merge_track(
        self,
        first_track: Track,
        first_track_merged: Track,
        second_track: Track,
        offset: RelativeOffsetCoordinate,
    ) -> None:
        track_dataset = create_track_dataset([first_track, second_track])
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, offset
        )
        result = geometry_dataset.add_all([first_track_merged])
        expected = create_geometry_dataset_from(
            [first_track_merged, second_track], offset
        )
        assert_track_geometry_dataset_equals(result, expected)

    @pytest.mark.parametrize("offset", [BASE_GEOMETRY, DEFAULT_TRACK_OFFSET])
    def test_remove_from_filled_dataset(
        self, first_track: Track, second_track: Track, offset: RelativeOffsetCoordinate
    ) -> None:
        track_dataset = create_track_dataset([first_track, second_track])
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, offset
        )
        result = geometry_dataset.remove([first_track.id.id])
        expected = create_geometry_dataset_from([second_track], offset)
        assert_track_geometry_dataset_equals(result, expected)

    @pytest.mark.parametrize("offset", [BASE_GEOMETRY, DEFAULT_TRACK_OFFSET])
    def test_remove_from_empty_dataset(
        self, first_track: Track, offset: RelativeOffsetCoordinate
    ) -> None:
        geometry_dataset = ShapelyTrackGeometryDataset(offset)
        result = geometry_dataset.remove([first_track.id.id])
        assert_track_geometry_dataset_equals(
            result, ShapelyTrackGeometryDataset(offset)
        )

    @pytest.mark.parametrize("offset", [BASE_GEOMETRY, DEFAULT_TRACK_OFFSET])
    def test_remove_missing(
        self, first_track: Track, second_track: Track, offset: RelativeOffsetCoordinate
    ) -> None:
        track_dataset = create_track_dataset([first_track])
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, offset
        )
        result = geometry_dataset.remove([second_track.id.id])
        expected = create_geometry_dataset_from([first_track], offset)
        assert_track_geometry_dataset_equals(result, expected)

    def test_intersection_points(
        self,
        single_detection_track: Track,
        not_intersecting_track: Track,
        first_track: Track,
        second_track: Track,
        not_intersecting_section: Section,
        first_section: Section,
        second_section: Section,
        third_section: Section,
        forth_section: Section,
    ) -> None:
        sections = [
            not_intersecting_section,
            first_section,
            second_section,
            third_section,
            forth_section,
        ]
        track_dataset = create_track_dataset(
            [single_detection_track, not_intersecting_track, first_track, second_track]
        )
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, BASE_GEOMETRY
        )
        result = geometry_dataset.intersection_points(sections)
        assert result == {
            first_track.id: [
                (
                    first_section.id,
                    IntersectionPoint(upper_index=1, relative_position=0.5),
                ),
                (
                    second_section.id,
                    IntersectionPoint(upper_index=2, relative_position=0.5),
                ),
                (
                    third_section.id,
                    IntersectionPoint(upper_index=3, relative_position=0.5),
                ),
                (
                    forth_section.id,
                    IntersectionPoint(upper_index=4, relative_position=0.25),
                ),
            ],
            second_track.id: [
                (
                    first_section.id,
                    IntersectionPoint(upper_index=1, relative_position=0.5),
                ),
                (
                    second_section.id,
                    IntersectionPoint(upper_index=2, relative_position=0.5),
                ),
                (
                    third_section.id,
                    IntersectionPoint(upper_index=3, relative_position=0.5),
                ),
                (
                    forth_section.id,
                    IntersectionPoint(upper_index=4, relative_position=0.25),
                ),
            ],
        }

    def test_intersecting_tracks(
        self,
        single_detection_track: Track,
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
            [single_detection_track, not_intersecting_track, first_track, second_track]
        )
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, BASE_GEOMETRY
        )
        result = geometry_dataset.intersecting_tracks(sections)
        assert result == {first_track.id, second_track.id}

    @patch(
        "OTAnalytics.plugin_datastore.track_geometry_store.shapely_store."
        "distance_on_track"
    )
    @pytest.mark.parametrize(
        "distance, upper_index, relative_position",
        [
            (0.0, 1, 0.0),
            (0.5, 1, 0.5),
            (1.0, 2, 0.0),
            (1.5, 2, 0.5),
            (2.0, 3, 0.0),
            (2.5, 3, 0.5),
            (3.0, 4, 0.0),
            (3.5, 4, 0.5),
            (4.0, 4, 1.0),
            (4.1, 4, 1.0),
        ],
    )
    def test_intersection_point_with_rounding_error(
        self,
        mock_distance_on_track: Mock,
        first_track: Track,
        first_section: Section,
        distance: float,
        upper_index: int,
        relative_position: float,
    ) -> None:
        """
        https://openproject.platomo.de/projects/otanalytics/work_packages/6836/activity
        """
        distances_to_create_geometry = [0, 1, 2, 3, 4]
        distance_to_create_event = [distance]
        distances = distances_to_create_geometry + distance_to_create_event
        mock_distance_on_track.side_effect = iter(distances)
        sections = [
            first_section,
        ]
        track_dataset = create_track_dataset([first_track])
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, BASE_GEOMETRY
        )
        result = geometry_dataset.intersection_points(sections)
        expected = {
            first_track.id: [
                (
                    first_section.id,
                    IntersectionPoint(
                        upper_index=upper_index,
                        relative_position=relative_position,
                    ),
                )
            ]
        }
        assert result == expected

    def test_as_dict(self, first_track: Track, second_track: Track) -> None:
        tracks = [first_track, second_track]
        track_dataset = create_track_dataset(tracks)
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, BASE_GEOMETRY
        )
        assert isinstance(geometry_dataset, ShapelyTrackGeometryDataset)
        result = geometry_dataset.as_dict()
        expected = (
            create_geometry_dataset_from(tracks, BASE_GEOMETRY)
            ._dataset[COLUMNS]
            .to_dict(orient="index")
        )
        assert result == expected

    def test_empty_on_empty_dataset(self) -> None:
        geometry_dataset = ShapelyTrackGeometryDataset(BASE_GEOMETRY)
        assert geometry_dataset.empty

    def test_empty_on_filled_dataset(self, first_track: Track) -> None:
        track_dataset = create_track_dataset([first_track])
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, BASE_GEOMETRY
        )
        assert isinstance(geometry_dataset, ShapelyTrackGeometryDataset)
        assert not geometry_dataset.empty

    def test_get_track_ids(self, first_track: Track) -> None:
        track_dataset = create_track_dataset([first_track])
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, BASE_GEOMETRY
        )
        assert isinstance(geometry_dataset, ShapelyTrackGeometryDataset)
        assert geometry_dataset.track_ids == {first_track.id.id}

    def test_contained_by_sections(
        self,
        contained_by_section_test_case: ContainedBySectionTestCase,
    ) -> None:
        track_dataset = create_track_dataset(contained_by_section_test_case.tracks)
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, BASE_GEOMETRY
        )
        result = geometry_dataset.contained_by_sections(
            contained_by_section_test_case.sections
        )
        assert result == contained_by_section_test_case.expected_result

    def test_get_for_existing(self, first_track: Track, second_track: Track) -> None:
        track_dataset = create_track_dataset([first_track, second_track])
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, BASE_GEOMETRY
        )
        result = geometry_dataset.get_for([first_track.id.id])
        expected = create_geometry_dataset_from([first_track], BASE_GEOMETRY)
        assert_track_geometry_dataset_equals(result, expected)

    def test_get_for_not_existing(
        self, first_track: Track, second_track: Track
    ) -> None:
        track_dataset = create_track_dataset([first_track, second_track])
        geometry_dataset = ShapelyTrackGeometryDataset.from_track_dataset(
            track_dataset, BASE_GEOMETRY
        )
        result = geometry_dataset.get_for(["not-existing-track"])
        expected = create_geometry_dataset_from([], BASE_GEOMETRY)
        assert_track_geometry_dataset_equals(result, expected)

    def test_add_invalid_track(
        self, single_detection_track_dataset: PandasTrackDataset
    ) -> None:
        empty_dataset = ShapelyTrackGeometryDataset(BASE_GEOMETRY)
        assert not empty_dataset.track_ids

        result = empty_dataset.add_all(single_detection_track_dataset)
        assert not result.track_ids
        assert result.empty

    def test_equals(self, first_track: Track, second_track: Track) -> None:
        first_track_dataset: TrackGeometryDataset = ShapelyTrackGeometryDataset(
            RelativeOffsetCoordinate(0, 0)
        ).add_all([first_track])
        first_track_dataset_different_offset: TrackGeometryDataset = (
            ShapelyTrackGeometryDataset(RelativeOffsetCoordinate(1, 1)).add_all(
                [first_track]
            )
        )
        second_track_dataset: TrackGeometryDataset = ShapelyTrackGeometryDataset(
            RelativeOffsetCoordinate(0, 0)
        ).add_all([second_track])

        assert first_track_dataset != second_track_dataset
        assert first_track_dataset == first_track_dataset
        assert first_track_dataset != first_track_dataset_different_offset
        assert first_track_dataset != 5


class TestProfiling:
    ROUNDS = 1
    ITERATIONS = 1
    WARMUP_ROUNDS = 0

    @pytest.fixture
    def tracks_15min(
        self, test_data_dir: Path, track_geometry_factory: TRACK_GEOMETRY_FACTORY
    ) -> TrackDataset:
        ottrk = test_data_dir / "OTCamera19_FR20_2023-05-24_07-00-00.ottrk"
        ottrk_parser = OttrkParser(
            PandasDetectionParser(PandasByMaxConfidence(), track_geometry_factory)
        )
        parse_result = ottrk_parser.parse(ottrk)
        return parse_result.tracks

    @pytest.fixture
    def sections(self, test_data_dir: Path) -> list[Section]:
        flow_file = test_data_dir / "OTCamera19_FR20_2023-05-24.otflow"
        flow_parser = OtFlowParser()
        sections, flows = flow_parser.parse(flow_file)
        return list(sections)

    @pytest.mark.skip
    def test_profile(
        self,
        benchmark: BenchmarkFixture,
        tracks_15min: TrackDataset,
        sections: list[Section],
    ) -> None:
        benchmark.pedantic(
            tracks_15min.intersecting_tracks,
            args=(sections, sections[0].get_offset(EventType.SECTION_ENTER)),
            rounds=self.ROUNDS,
            iterations=self.ITERATIONS,
            warmup_rounds=self.WARMUP_ROUNDS,
        )
