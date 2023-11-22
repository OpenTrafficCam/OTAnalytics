from dataclasses import dataclass
from unittest.mock import Mock, call

import pytest

from OTAnalytics.domain.geometry import (
    Coordinate,
    DirectionVector2D,
    RelativeOffsetCoordinate,
    apply_offset,
)
from OTAnalytics.domain.section import (
    Area,
    LineSection,
    Section,
    SectionId,
    SectionType,
)
from OTAnalytics.domain.track import Detection, Track
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_intersect.shapely.create_intersection_events import (
    ShapelyGeometryBuilder,
    ShapelyIntersectAreaByTrackPoints,
    ShapelyIntersectBySmallestTrackSegments,
    ShapelyTrackLookupTable,
    separate_sections,
)
from tests.conftest import TrackBuilder


@dataclass
class _ExpectedEventCoord:
    detection_index: int
    x: float
    y: float
    event_type: EventType = EventType.SECTION_ENTER

    @staticmethod
    def from_detection(
        detection: Detection,
        detection_index: int,
        event_type: EventType,
        offset: tuple[float, float],
    ) -> "_ExpectedEventCoord":
        x, y = apply_offset(
            detection.x,
            detection.y,
            detection.w,
            detection.h,
            RelativeOffsetCoordinate(offset[0], offset[1]),
        )
        return _ExpectedEventCoord(detection_index, x, y, event_type)


@dataclass
class _TestCase:
    track: Track
    section: Section
    expected_event_coords: list[_ExpectedEventCoord]
    direction_vectors: list[tuple[float, float]]

    def assert_valid(self, event_results: list, event_builder: Mock) -> None:
        assert len(event_results) == len(self.expected_event_coords)
        if self.expected_event_coords:
            self._assert_has_calls(event_builder)
        else:
            self._assert_no_calls(event_builder)

    def _assert_has_calls(self, event_builder: Mock) -> None:
        event_builder.add_road_user_type.assert_called_once_with(
            self.track.classification
        )
        assert event_builder.add_direction_vector.call_args_list == [
            call(DirectionVector2D(x, y)) for x, y in self.direction_vectors
        ]
        assert event_builder.add_event_type.call_args_list == [
            call(expected_event.event_type)
            for expected_event in self.expected_event_coords
        ]
        assert event_builder.add_event_coordinate.call_args_list == [
            call(expected_event.x, expected_event.y)
            for expected_event in self.expected_event_coords
        ]
        assert event_builder.create_event.call_args_list == [
            call(self.track.detections[expected_event.detection_index])
            for expected_event in self.expected_event_coords
        ]

    def _assert_no_calls(self, event_builder: Mock) -> None:
        event_builder.add_road_user_type.assert_not_called()
        event_builder.add_direction_vector.assert_not_called()
        event_builder.add_event_type.assert_not_called()
        event_builder.add_event.assert_not_called()
        event_builder.add_event.assert_not_called()


def create_section(
    coordinates: list[tuple[float, float]],
    section_type: SectionType,
    offset: tuple[float, float] = (0, 0),
) -> Section:
    section_id = SectionId("N")
    name = section_id.id
    offset_x, offset_y = offset
    offset_coords = {
        EventType.SECTION_ENTER: RelativeOffsetCoordinate(offset_x, offset_y)
    }
    _coordinates = [Coordinate(x, y) for x, y in coordinates]
    match section_type:
        case SectionType.LINE:
            return LineSection(
                id=section_id,
                name=name,
                relative_offset_coordinates=offset_coords,
                plugin_data={},
                coordinates=_coordinates,
            )

        case SectionType.AREA:
            return Area(
                id=section_id,
                name=name,
                relative_offset_coordinates=offset_coords,
                plugin_data={},
                coordinates=_coordinates,
            )
        case _:
            raise TypeError(f"Section of type {section_type} does not exist!")


@pytest.fixture
def track(track_builder: TrackBuilder) -> Track:
    classification = "car"
    track_id = "1"

    track_builder.add_track_class(classification)
    track_builder.add_detection_class(classification)
    track_builder.add_track_id(track_id)
    track_builder.add_wh_bbox(1, 1)

    track_builder.add_frame(1)
    track_builder.add_second(0)
    track_builder.add_xy_bbox(0.0, 1.0)
    track_builder.append_detection()

    track_builder.add_frame(2)
    track_builder.add_second(1)
    track_builder.add_xy_bbox(1.0, 1.0)
    track_builder.append_detection()

    track_builder.add_frame(3)
    track_builder.add_second(2)
    track_builder.add_xy_bbox(2.0, 1.0)
    track_builder.append_detection()

    return track_builder.build_track()


@pytest.fixture
def closed_track(track_builder: TrackBuilder) -> Track:
    classification = "car"
    track_id = "2"

    track_builder.add_track_class(classification)
    track_builder.add_detection_class(classification)
    track_builder.add_track_id(track_id)

    track_builder.add_frame(1)
    track_builder.add_second(1)
    track_builder.add_xy_bbox(1, 1)
    track_builder.append_detection()

    track_builder.add_frame(2)
    track_builder.add_second(2)
    track_builder.add_xy_bbox(2, 1)
    track_builder.append_detection()

    track_builder.add_frame(3)
    track_builder.add_second(3)
    track_builder.add_xy_bbox(2, 2)
    track_builder.append_detection()

    track_builder.add_frame(5)
    track_builder.add_second(5)
    track_builder.add_xy_bbox(1, 2)
    track_builder.append_detection()

    track_builder.add_frame(5)
    track_builder.add_second(5)
    track_builder.add_xy_bbox(1, 1)
    track_builder.append_detection()
    return track_builder.build_track()


@pytest.fixture
def test_case_track_line_section(
    track: Track,
) -> _TestCase:
    offset = (0, 0.5)
    section = create_section([(1.5, 0), (1.5, 1.5)], SectionType.LINE, offset)
    detection_index = 2
    detection = track.detections[detection_index]
    expected_event_coords = [
        _ExpectedEventCoord.from_detection(
            detection,
            detection_index=detection_index,
            offset=offset,
            event_type=EventType.SECTION_ENTER,
        ),
    ]
    direction_vectors = [(1.0, 0.0)]

    return _TestCase(track, section, expected_event_coords, direction_vectors)


@pytest.fixture
def test_case_closed_track_line_section(
    closed_track: Track,
) -> _TestCase:
    section = create_section([(0, 1.5), (3, 1.5)], SectionType.LINE)
    expected_event_coords = [
        _ExpectedEventCoord(2, 2.0, 2.0),
        _ExpectedEventCoord(4, 1.0, 1.0),
    ]
    expected_dir_vectors = [(0.0, 1.0), (0.0, -1.0)]
    return _TestCase(closed_track, section, expected_event_coords, expected_dir_vectors)


@pytest.fixture
def test_case_line_section_no_intersection(track: Track) -> _TestCase:
    section = create_section([(0, 0), (10, 0)], SectionType.LINE)

    return _TestCase(track, section, [], [])


class TestShapelyIntersectBySmallestTrackSegments:
    def _create_intersector(
        self, offset: RelativeOffsetCoordinate
    ) -> ShapelyIntersectBySmallestTrackSegments:
        geometry_builder = ShapelyGeometryBuilder()
        track_lookup_table = ShapelyTrackLookupTable(dict(), geometry_builder, offset)

        return ShapelyIntersectBySmallestTrackSegments(
            geometry_builder, track_lookup_table
        )

    @pytest.mark.parametrize(
        "test_case_name",
        [
            "test_case_track_line_section",
            "test_case_closed_track_line_section",
            "test_case_line_section_no_intersection",
        ],
    )
    def test_intersect(
        self,
        test_case_name: str,
        request: pytest.FixtureRequest,
    ) -> None:
        test_case: _TestCase
        test_case = request.getfixturevalue(test_case_name)

        event = Mock()
        event_builder = Mock()
        event_builder.create_event.return_value = event

        intersector = self._create_intersector(
            test_case.section.get_offset(EventType.SECTION_ENTER)
        )
        result_events = intersector.intersect(
            [test_case.track], test_case.section, event_builder
        )

        test_case.assert_valid(result_events, event_builder)


class TestShapelyIntersectAreaByTrackPoints:
    def _create_intersector(
        self, offset: RelativeOffsetCoordinate
    ) -> ShapelyIntersectAreaByTrackPoints:
        geometry_builder = ShapelyGeometryBuilder()
        track_lookup_table = ShapelyTrackLookupTable(dict(), geometry_builder, offset)

        return ShapelyIntersectAreaByTrackPoints(geometry_builder, track_lookup_table)

    @pytest.fixture
    def straight_track(self, track_builder: TrackBuilder) -> Track:
        track_builder.add_wh_bbox(0.5, 0.5)
        track_builder.add_xy_bbox(1.0, 1.0)
        track_builder.append_detection()

        track_builder.add_xy_bbox(2.0, 1.0)
        track_builder.add_frame(2)
        track_builder.add_microsecond(1)
        track_builder.append_detection()

        track_builder.add_xy_bbox(3.0, 1.0)
        track_builder.add_frame(3)
        track_builder.add_microsecond(2)
        track_builder.append_detection()

        return track_builder.build_track()

    @pytest.fixture
    def complex_track(self, track_builder: TrackBuilder) -> Track:
        track_builder.add_xy_bbox(1.0, 1.0)
        track_builder.append_detection()

        track_builder.add_xy_bbox(2.0, 1.0)
        track_builder.add_frame(2)
        track_builder.add_microsecond(1)
        track_builder.append_detection()

        track_builder.add_xy_bbox(2.0, 1.5)
        track_builder.add_frame(3)
        track_builder.add_microsecond(2)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.0, 1.5)
        track_builder.add_frame(4)
        track_builder.add_microsecond(3)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.0, 2.0)
        track_builder.add_frame(5)
        track_builder.add_microsecond(4)
        track_builder.append_detection()

        track_builder.add_xy_bbox(2.0, 2.0)
        track_builder.add_frame(5)
        track_builder.add_microsecond(4)
        track_builder.append_detection()

        return track_builder.build_track()

    @pytest.fixture
    def test_case_track_starts_outside_section(
        self, straight_track: Track
    ) -> _TestCase:
        offset = (0.0, 0.5)
        section = create_section(
            [(1.5, 0.5), (1.5, 1.5), (2.5, 1.5), (2.5, 0.5), (1.5, 0.5)],
            SectionType.AREA,
            offset,
        )
        expected_event_coords = [
            _ExpectedEventCoord.from_detection(
                straight_track.detections[1], 1, EventType.SECTION_ENTER, offset
            ),
            _ExpectedEventCoord.from_detection(
                straight_track.detections[2], 2, EventType.SECTION_LEAVE, offset
            ),
        ]
        expected_direction_vectors = [(1.0, 0.0), (1.0, 0)]
        return _TestCase(
            straight_track, section, expected_event_coords, expected_direction_vectors
        )

    @pytest.fixture
    def test_case_track_starts_inside_section(self, straight_track: Track) -> _TestCase:
        section = create_section(
            [(0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)],
            SectionType.AREA,
        )
        expected_event_coords = [
            _ExpectedEventCoord(0, 1.0, 1.0, EventType.SECTION_ENTER),
            _ExpectedEventCoord(1, 2.0, 1.0, EventType.SECTION_LEAVE),
        ]
        expected_direction_vectors = [(1.0, 0.0), (1.0, 0.0)]
        return _TestCase(
            straight_track, section, expected_event_coords, expected_direction_vectors
        )

    @pytest.fixture
    def test_case_track_is_inside_section(self, straight_track: Track) -> _TestCase:
        section = create_section(
            [(0.0, 0.0), (0.0, 2.0), (4.0, 2.0), (4.0, 0.0), (0.0, 0.0)],
            SectionType.AREA,
        )
        expected_event_coords = [
            _ExpectedEventCoord(0, 1.0, 1.0, EventType.SECTION_ENTER)
        ]
        expected_direction_vectors = [(1.0, 0.0)]
        return _TestCase(
            straight_track, section, expected_event_coords, expected_direction_vectors
        )

    @pytest.fixture
    def test_case_starts_outside_stays_inside(self, straight_track: Track) -> _TestCase:
        section = create_section(
            [(1.5, 0.5), (1.5, 1.5), (4.0, 1.5), (4.0, 0.5), (1.5, 0.5)],
            SectionType.AREA,
        )
        expected_event_coords = [
            _ExpectedEventCoord(1, 2.0, 1.0, EventType.SECTION_ENTER)
        ]
        expected_direction_vectors = [(1.0, 0.0)]
        return _TestCase(
            straight_track, section, expected_event_coords, expected_direction_vectors
        )

    @pytest.fixture
    def test_case_track_starts_outside_section_multiple_intersections(
        self, complex_track: Track
    ) -> _TestCase:
        pass
        section = create_section(
            [(1.5, 0.5), (1.5, 2.5), (2.5, 2.5), (2.5, 0.5), (1.5, 0.5)],
            SectionType.AREA,
        )
        expected_event_coords = [
            _ExpectedEventCoord(1, 2.0, 1.0, EventType.SECTION_ENTER),
            _ExpectedEventCoord(3, 1.0, 1.5, EventType.SECTION_LEAVE),
            _ExpectedEventCoord(5, 2.0, 2.0, EventType.SECTION_ENTER),
        ]
        expected_direction_vectors = [(1.0, 0.0), (-1.0, 0), (1.0, 0.0)]
        return _TestCase(
            complex_track, section, expected_event_coords, expected_direction_vectors
        )

    @pytest.fixture
    def test_case_track_starts_inside_section_multiple_intersections(
        self, complex_track: Track
    ) -> _TestCase:
        pass
        section = create_section(
            [(0.5, 0.5), (0.5, 2.5), (1.5, 2.5), (1.5, 0.5), (0.5, 0.5)],
            SectionType.AREA,
        )
        expected_event_coords = [
            _ExpectedEventCoord(0, 1.0, 1.0, EventType.SECTION_ENTER),
            _ExpectedEventCoord(1, 2.0, 1.0, EventType.SECTION_LEAVE),
            _ExpectedEventCoord(3, 1.0, 1.5, EventType.SECTION_ENTER),
            _ExpectedEventCoord(5, 2.0, 2.0, EventType.SECTION_LEAVE),
        ]
        expected_direction_vectors = [(1.0, 0.0), (1.0, 0.0), (-1.0, 0), (1, 0)]
        return _TestCase(
            complex_track, section, expected_event_coords, expected_direction_vectors
        )

    @pytest.fixture
    def test_case_intersect_closed_track(
        self, track_builder: TrackBuilder
    ) -> _TestCase:
        track_builder.add_xy_bbox(1.0, 1.0)
        track_builder.append_detection()

        track_builder.add_xy_bbox(2.0, 1.0)
        track_builder.add_frame(2)
        track_builder.add_microsecond(1)
        track_builder.append_detection()

        track_builder.add_xy_bbox(2.0, 1.5)
        track_builder.add_frame(3)
        track_builder.add_microsecond(2)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.0, 1.5)
        track_builder.add_frame(4)
        track_builder.add_microsecond(3)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.0, 1.0)
        track_builder.add_frame(5)
        track_builder.add_microsecond(4)
        track_builder.append_detection()

        track = track_builder.build_track()
        section = create_section(
            [(1.5, 0.5), (1.5, 2.0), (2.5, 2.0), (2.5, 0.5), (1.5, 0.5)],
            SectionType.AREA,
        )
        expected_event_coords = [
            _ExpectedEventCoord(1, 2.0, 1.0, EventType.SECTION_ENTER),
            _ExpectedEventCoord(3, 1.0, 1.5, EventType.SECTION_LEAVE),
        ]
        expected_direction_vectors = [(1.0, 0.0), (-1.0, 0.0)]
        return _TestCase(
            track, section, expected_event_coords, expected_direction_vectors
        )

    @pytest.mark.parametrize(
        "test_case_name",
        [
            "test_case_track_starts_outside_section",
            "test_case_track_starts_inside_section",
            "test_case_track_is_inside_section",
            "test_case_starts_outside_stays_inside",
            "test_case_track_starts_outside_section_multiple_intersections",
            "test_case_track_starts_inside_section_multiple_intersections",
            "test_case_intersect_closed_track",
        ],
    )
    def test_intersect(
        self,
        test_case_name: str,
        request: pytest.FixtureRequest,
    ) -> None:
        test_case: _TestCase
        test_case = request.getfixturevalue(test_case_name)

        event = Mock()
        event_builder = Mock()
        event_builder.create_event.return_value = event

        intersector = self._create_intersector(
            test_case.section.get_offset(EventType.SECTION_ENTER)
        )
        result_events = intersector.intersect(
            [test_case.track], test_case.section, event_builder
        )

        test_case.assert_valid(result_events, event_builder)


def test_separate_sections_with_valid_args() -> None:
    first_line_section = Mock(spec=LineSection)
    second_line_section = Mock(spec=LineSection)

    first_area_section = Mock(spec=Area)
    second_area_section = Mock(spec=Area)
    line_sections, area_sections = separate_sections(
        [
            first_line_section,
            first_area_section,
            second_line_section,
            second_area_section,
        ]
    )
    assert line_sections == [first_line_section, second_line_section]
    assert area_sections == [first_area_section, second_area_section]


def test_separate_sections_with_invalid_args() -> None:
    section = Mock(spec=LineSection)
    invalid_section = Mock()

    with pytest.raises(TypeError):
        separate_sections([section, invalid_section])
