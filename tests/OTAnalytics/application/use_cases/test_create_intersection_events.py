from dataclasses import dataclass
from datetime import datetime
from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.use_cases.create_intersection_events import (
    IntersectAreaByTrackPoints,
    IntersectByIntersectionPoints,
    separate_sections,
)
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
from OTAnalytics.domain.track_dataset.track_dataset import (
    IntersectionPoint,
    TrackDataset,
)
from OTAnalytics.domain.types import EventType
from tests.utils.builders.track_builder import TrackBuilder


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


class _TestCase:
    def __init__(
        self,
        track: Track,
        track_dataset: Mock,
        section: Section,
        expected_event_coords: list[_ExpectedEventCoord],
        direction_vectors: list[tuple[float, float]],
    ):
        self.track = track
        self.track_dataset = track_dataset
        self.section = section
        self.expected_event_coords = expected_event_coords
        self.direction_vectors = direction_vectors

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
        event_builder.add_interpolated_occurrence.assert_not_called()
        event_builder.add_interpolated_event_coordinate.assert_not_called()


class LineSectionTestCase(_TestCase):
    def __init__(
        self,
        track: Track,
        track_dataset: Mock,
        section: Section,
        expected_event_coords: list[_ExpectedEventCoord],
        direction_vectors: list[tuple[float, float]],
        expected_interpolated_occurrences: list[datetime],
        expected_interpolated_coords: list[Coordinate],
    ):
        super().__init__(
            track, track_dataset, section, expected_event_coords, direction_vectors
        )
        self.expected_interpolated_occurrences = expected_interpolated_occurrences
        self.expected_interpolated_coords = expected_interpolated_coords

    def assert_valid(self, event_results: list, event_builder: Mock) -> None:
        super().assert_valid(event_results, event_builder)
        self._assert_valid(event_results, event_builder)

    def _assert_valid(self, event_results: list, event_builder: Mock) -> None:
        self.track_dataset.intersection_points.assert_called_once_with(
            [self.section], self.section.get_offset(EventType.SECTION_ENTER)
        )
        if self.expected_event_coords:
            self._event_builder_has_calls(event_builder)

    def _event_builder_has_calls(self, event_builder: Mock) -> None:
        assert event_builder.add_interpolated_occurrence.call_args_list == [
            call(occurrence) for occurrence in self.expected_interpolated_occurrences
        ]
        assert event_builder.add_interpolated_event_coordinate.call_args_list == [
            call(coord.x, coord.y) for coord in self.expected_interpolated_coords
        ]


class AreaSectionTestCase(_TestCase):
    def __init__(
        self,
        track: Track,
        track_dataset: Mock,
        section: Section,
        expected_event_coords: list[_ExpectedEventCoord],
        direction_vectors: list[tuple[float, float]],
    ):
        super().__init__(
            track, track_dataset, section, expected_event_coords, direction_vectors
        )

    def assert_valid(self, event_results: list, event_builder: Mock) -> None:
        super().assert_valid(event_results, event_builder)
        self._assert_valid()

    def _assert_valid(self) -> None:
        self.track_dataset.contained_by_sections.assert_called_once_with(
            [self.section], self.section.get_offset(EventType.SECTION_ENTER)
        )

    def _event_builder_has_calls(self, event_builder: Mock) -> None:
        assert event_builder.add_interpolated_occurrence.call_args_list == [
            call(self.track.get_detection(event_coords.detection_index).occurrence)
            for event_coords in self.expected_event_coords
        ]
        assert event_builder.add_interpolated_event_coordinate.call_args_list == [
            call(event_coord.x, event_coord.y)
            for event_coord in self.expected_event_coords
        ]


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
def test_case_track_line_section(track: Track) -> _TestCase:
    offset = (0, 0.5)
    section = create_section([(1.5, 0), (1.5, 1.5)], SectionType.LINE, offset)
    detection_index = 2
    ip = IntersectionPoint(upper_index=detection_index, relative_position=0.5)
    prev_detection = track.detections[ip.lower_index]
    detection = track.detections[ip.upper_index]
    track_dataset = Mock(spec=TrackDataset)
    track_dataset.intersection_points.return_value = {track.id: [(section.id, ip)]}
    track_dataset.get_for.return_value = track
    expected_event_coord = _ExpectedEventCoord.from_detection(
        detection,
        detection_index=ip.upper_index,
        offset=offset,
        event_type=EventType.SECTION_ENTER,
    )

    expected_event_coords = [expected_event_coord]
    direction_vectors = [(1.0, 0.0)]
    expected_interpolated_occurrence = (
        prev_detection.occurrence
        + ip.relative_position * (detection.occurrence - prev_detection.occurrence)
    )

    prev_coord = prev_detection.get_coordinate(RelativeOffsetCoordinate(*offset))
    current_coord = detection.get_coordinate(RelativeOffsetCoordinate(*offset))

    expected_interpolated_x = prev_coord.x + ip.relative_position * (
        current_coord.x - prev_coord.x
    )
    expected_interpolated_y = prev_coord.y + ip.relative_position * (
        current_coord.y - prev_coord.y
    )
    expected_interpolated_coord = Coordinate(
        expected_interpolated_x, expected_interpolated_y
    )

    return LineSectionTestCase(
        track,
        track_dataset,
        section,
        expected_event_coords,
        direction_vectors,
        [expected_interpolated_occurrence],
        [expected_interpolated_coord],
    )


@pytest.fixture
def test_case_closed_track_line_section(
    closed_track: Track,
) -> _TestCase:
    section = create_section([(0, 1.5), (3, 1.5)], SectionType.LINE)
    track_dataset = Mock(spec=TrackDataset)
    track_dataset.intersection_points.return_value = {
        closed_track.id: [
            (section.id, IntersectionPoint(upper_index=2, relative_position=0)),
            (section.id, IntersectionPoint(upper_index=4, relative_position=0)),
        ]
    }
    track_dataset.get_for.return_value = closed_track
    expected_event_coords = [
        _ExpectedEventCoord(2, 2.0, 2.0),
        _ExpectedEventCoord(4, 1.0, 1.0),
    ]
    expected_dir_vectors = [(0.0, 1.0), (0.0, -1.0)]
    return _TestCase(
        closed_track,
        track_dataset,
        section,
        expected_event_coords,
        expected_dir_vectors,
    )


@pytest.fixture
def test_case_line_section_no_intersection(track: Track) -> _TestCase:
    section = create_section([(0, 0), (10, 0)], SectionType.LINE)
    track_dataset = Mock(spec=TrackDataset)
    track_dataset.intersection_points.return_value = {}
    track_dataset.get_for.return_value = track

    return _TestCase(track, track_dataset, section, [], [])


class TestIntersectByIntersectionPoints:
    def _create_intersector(self) -> IntersectByIntersectionPoints:
        return IntersectByIntersectionPoints()

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

        intersector = self._create_intersector()
        result_events = intersector.intersect(
            test_case.track_dataset, [test_case.section], event_builder
        )

        test_case.assert_valid(result_events, event_builder)


class TestIntersectAreaByTrackPoints:
    def _create_intersector(self) -> IntersectAreaByTrackPoints:
        return IntersectAreaByTrackPoints()

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
        track_dataset = Mock(spec=TrackDataset)
        track_dataset.contained_by_sections.return_value = {
            straight_track.id: [(section.id, [False, True, False])]
        }
        track_dataset.get_for.return_value = straight_track
        expected_event_coords = [
            _ExpectedEventCoord.from_detection(
                straight_track.detections[1], 1, EventType.SECTION_ENTER, offset
            ),
            _ExpectedEventCoord.from_detection(
                straight_track.detections[2], 2, EventType.SECTION_LEAVE, offset
            ),
        ]
        expected_direction_vectors = [(1.0, 0.0), (1.0, 0)]
        return AreaSectionTestCase(
            straight_track,
            track_dataset,
            section,
            expected_event_coords,
            expected_direction_vectors,
        )

    @pytest.fixture
    def test_case_track_starts_inside_section(self, straight_track: Track) -> _TestCase:
        section = create_section(
            [(0.5, 0.5), (0.5, 1.5), (1.5, 1.5), (1.5, 0.5), (0.5, 0.5)],
            SectionType.AREA,
        )
        track_dataset = Mock(spec=TrackDataset)
        track_dataset.contained_by_sections.return_value = {
            straight_track.id: [(section.id, [True, False, False])]
        }
        track_dataset.get_for.return_value = straight_track
        expected_event_coords = [
            _ExpectedEventCoord(0, 1.0, 1.0, EventType.SECTION_ENTER),
            _ExpectedEventCoord(1, 2.0, 1.0, EventType.SECTION_LEAVE),
        ]
        expected_direction_vectors = [(1.0, 0.0), (1.0, 0.0)]
        return AreaSectionTestCase(
            straight_track,
            track_dataset,
            section,
            expected_event_coords,
            expected_direction_vectors,
        )

    @pytest.fixture
    def test_case_track_is_inside_section(self, straight_track: Track) -> _TestCase:
        section = create_section(
            [(0.0, 0.0), (0.0, 2.0), (4.0, 2.0), (4.0, 0.0), (0.0, 0.0)],
            SectionType.AREA,
        )
        track_dataset = Mock(spec=TrackDataset)
        track_dataset.contained_by_sections.return_value = {
            straight_track.id: [(section.id, [True, True, True])]
        }
        track_dataset.get_for.return_value = straight_track
        expected_event_coords = [
            _ExpectedEventCoord(0, 1.0, 1.0, EventType.SECTION_ENTER)
        ]
        expected_direction_vectors = [(1.0, 0.0)]
        return AreaSectionTestCase(
            straight_track,
            track_dataset,
            section,
            expected_event_coords,
            expected_direction_vectors,
        )

    @pytest.fixture
    def test_case_starts_outside_stays_inside(self, straight_track: Track) -> _TestCase:
        section = create_section(
            [(1.5, 0.5), (1.5, 1.5), (4.0, 1.5), (4.0, 0.5), (1.5, 0.5)],
            SectionType.AREA,
        )
        track_dataset = Mock(spec=TrackDataset)
        track_dataset.contained_by_sections.return_value = {
            straight_track.id: [(section.id, [False, True, True])]
        }
        track_dataset.get_for.return_value = straight_track
        expected_event_coords = [
            _ExpectedEventCoord(1, 2.0, 1.0, EventType.SECTION_ENTER)
        ]
        expected_direction_vectors = [(1.0, 0.0)]
        return AreaSectionTestCase(
            straight_track,
            track_dataset,
            section,
            expected_event_coords,
            expected_direction_vectors,
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
        track_dataset = Mock(spec=TrackDataset)
        track_dataset.contained_by_sections.return_value = {
            complex_track.id: [(section.id, [False, True, True, False, False, True])]
        }
        track_dataset.get_for.return_value = complex_track
        expected_event_coords = [
            _ExpectedEventCoord(1, 2.0, 1.0, EventType.SECTION_ENTER),
            _ExpectedEventCoord(3, 1.0, 1.5, EventType.SECTION_LEAVE),
            _ExpectedEventCoord(5, 2.0, 2.0, EventType.SECTION_ENTER),
        ]
        expected_direction_vectors = [(1.0, 0.0), (-1.0, 0), (1.0, 0.0)]
        return AreaSectionTestCase(
            complex_track,
            track_dataset,
            section,
            expected_event_coords,
            expected_direction_vectors,
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
        track_dataset = Mock(spec=TrackDataset)
        track_dataset.contained_by_sections.return_value = {
            complex_track.id: [(section.id, [True, False, False, True, True, False])]
        }
        track_dataset.get_for.return_value = complex_track
        expected_event_coords = [
            _ExpectedEventCoord(0, 1.0, 1.0, EventType.SECTION_ENTER),
            _ExpectedEventCoord(1, 2.0, 1.0, EventType.SECTION_LEAVE),
            _ExpectedEventCoord(3, 1.0, 1.5, EventType.SECTION_ENTER),
            _ExpectedEventCoord(5, 2.0, 2.0, EventType.SECTION_LEAVE),
        ]
        expected_direction_vectors = [(1.0, 0.0), (1.0, 0.0), (-1.0, 0), (1, 0)]
        return AreaSectionTestCase(
            complex_track,
            track_dataset,
            section,
            expected_event_coords,
            expected_direction_vectors,
        )

    @pytest.fixture
    def test_case_intersect_closed_track(self, closed_track: Track) -> _TestCase:
        section = create_section(
            [(1.5, 0.5), (1.5, 2.0), (2.5, 2.0), (2.5, 0.5), (1.5, 0.5)],
            SectionType.AREA,
        )
        track_dataset = Mock(spec=TrackDataset)
        track_dataset.contained_by_sections.return_value = {
            closed_track.id: [(section.id, [False, True, False, False, False])]
        }
        track_dataset.get_for.return_value = closed_track
        expected_event_coords = [
            _ExpectedEventCoord(1, 2.0, 1.0, EventType.SECTION_ENTER),
            _ExpectedEventCoord(2, 2.0, 2.0, EventType.SECTION_LEAVE),
        ]
        expected_direction_vectors = [(1.0, 0.0), (0.0, 1.0)]
        return AreaSectionTestCase(
            closed_track,
            track_dataset,
            section,
            expected_event_coords,
            expected_direction_vectors,
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

        intersector = self._create_intersector()
        result_events = intersector.intersect(
            test_case.track_dataset, [test_case.section], event_builder
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
