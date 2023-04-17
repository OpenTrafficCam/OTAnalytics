from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from OTAnalytics.domain.event import Event, EventType, SectionEventBuilder
from OTAnalytics.domain.geometry import (
    Coordinate,
    DirectionVector2D,
    ImageCoordinate,
    Line,
    RelativeOffsetCoordinate,
)
from OTAnalytics.domain.intersect import (
    IntersectAreaByTrackPoints,
    IntersectBySmallTrackComponents,
    IntersectBySplittingTrackLine,
    IntersectImplementation,
    Intersector,
)
from OTAnalytics.domain.section import Area, LineSection, SectionId
from OTAnalytics.domain.track import Detection, Track, TrackId
from tests.conftest import EventBuilder, TrackBuilder


@pytest.fixture
def detection() -> Detection:
    return Detection(
        classification="car",
        confidence=0.5,
        x=0.0,
        y=5.0,
        w=15.3,
        h=30.5,
        frame=1,
        occurrence=datetime(2022, 1, 1, 0, 0, 0, 0),
        input_file_path=Path("path/to/myhostname_something.otdet"),
        interpolated_detection=False,
        track_id=TrackId(1),
    )


@pytest.fixture
def track() -> Track:
    track_id = TrackId(1)

    detection_1 = Detection(
        classification="car",
        confidence=0.5,
        x=0.0,
        y=5.0,
        w=15.3,
        h=30.5,
        frame=1,
        occurrence=datetime(2022, 1, 1, 0, 0, 0, 0),
        input_file_path=Path("path/to/myhostname_something.otdet"),
        interpolated_detection=False,
        track_id=TrackId(1),
    )
    detection_2 = Detection(
        classification="car",
        confidence=0.5,
        x=10.0,
        y=5.0,
        w=15.3,
        h=30.5,
        frame=2,
        occurrence=datetime(2022, 1, 1, 0, 0, 0, 1),
        input_file_path=Path("path/to/myhostname_something.otdet"),
        interpolated_detection=False,
        track_id=TrackId(1),
    )
    detection_3 = Detection(
        classification="car",
        confidence=0.5,
        x=15.0,
        y=5.0,
        w=15.3,
        h=30.5,
        frame=3,
        occurrence=datetime(2022, 1, 1, 0, 0, 0, 2),
        input_file_path=Path("path/to/myhostname_something.otdet"),
        interpolated_detection=False,
        track_id=TrackId(1),
    )
    detection_4 = Detection(
        classification="car",
        confidence=0.5,
        x=20.0,
        y=5.0,
        w=15.3,
        h=30.5,
        frame=4,
        occurrence=datetime(2022, 1, 1, 0, 0, 0, 3),
        input_file_path=Path("path/to/myhostname_something.otdet"),
        interpolated_detection=False,
        track_id=TrackId(1),
    )
    detection_5 = Detection(
        classification="car",
        confidence=0.5,
        x=25.0,
        y=5.0,
        w=15.3,
        h=30.5,
        frame=5,
        occurrence=datetime(2022, 1, 1, 0, 0, 0, 4),
        input_file_path=Path("path/to/myhostname_something.otdet"),
        interpolated_detection=False,
        track_id=TrackId(1),
    )
    return Track(
        track_id,
        "car",
        [detection_1, detection_2, detection_3, detection_4, detection_5],
    )


class TestIntersector:
    def test_select_coordinate_in_detection(self, detection: Detection) -> None:
        offset = RelativeOffsetCoordinate(0.5, 0.5)
        coordinate = Intersector._select_coordinate_in_detection(detection, offset)
        assert coordinate.x == detection.x + detection.w * 0.5
        assert coordinate.y == detection.y + detection.h * 0.5

    def test_extract_offset_from_section(self) -> None:
        offset = RelativeOffsetCoordinate(0, 0)
        section = LineSection(
            SectionId("N"),
            {EventType.SECTION_ENTER: offset},
            {},
            start=Coordinate(0, 0),
            end=Coordinate(1, 1),
        )
        result = Intersector._extract_offset_from_section(
            section, EventType.SECTION_ENTER
        )
        assert result == offset


class TestIntersectBySplittingTrackLine:
    def test_intersect(self, detection: Detection, track: Track) -> None:
        # Setup mock intersection implementation
        mock_implementation = Mock(spec=IntersectImplementation)
        intersection_result: list[Line] = [
            Line([Coordinate(0, 5), Coordinate(5, 5)]),
            Line([Coordinate(5, 5), Coordinate(10, 5)]),
        ]
        mock_implementation.split_line_with_line.return_value = intersection_result

        # Setup event builder
        event_builder = SectionEventBuilder()
        event_builder.add_section_id(SectionId("N"))
        event_builder.add_event_type(EventType.SECTION_ENTER)
        event_builder.add_direction_vector(detection, detection)

        line_section = LineSection(
            id=SectionId("N"),
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            start=Coordinate(5, 0),
            end=Coordinate(5, 10),
        )

        intersector = IntersectBySplittingTrackLine(mock_implementation, line_section)
        result_events = intersector.intersect(track, event_builder)
        assert result_events is not None

        result_event = result_events[0]
        expected_detection = track.detections[1]

        assert len(result_events) == 1
        assert result_event.road_user_id == expected_detection.track_id.id
        assert result_event.road_user_type == expected_detection.classification
        assert result_event.hostname == "myhostname"
        assert result_event.occurrence == expected_detection.occurrence
        assert result_event.frame_number == expected_detection.frame
        assert result_event.section_id == line_section.id
        assert result_event.event_type == EventType.SECTION_ENTER
        assert result_event.direction_vector.x1 == 0
        assert result_event.direction_vector.x2 == 0
        assert result_event.video_name == expected_detection.input_file_path.name


class TestIntersectBySmallTrackComponents:
    def test_intersect(self, detection: Detection, track: Track) -> None:
        # Setup mock intersection implementation
        mock_implementation = Mock(spec=IntersectImplementation)
        mock_implementation.line_intersects_line.side_effect = [
            True,
            True,
            False,
            False,
            False,
            False,
        ]

        # Setup event builder
        event_builder = SectionEventBuilder()
        event_builder.add_section_id(SectionId("N"))
        event_builder.add_event_type(EventType.SECTION_ENTER)
        event_builder.add_direction_vector(detection, detection)

        line_section = LineSection(
            id=SectionId("N"),
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            start=Coordinate(5, 0),
            end=Coordinate(5, 10),
        )

        intersector = IntersectBySmallTrackComponents(mock_implementation, line_section)
        result_events = intersector.intersect(track, event_builder)
        assert result_events is not None

        result_event = result_events[0]
        expected_detection = track.detections[1]
        assert len(result_events) == 1
        assert result_event.road_user_id == expected_detection.track_id.id
        assert result_event.road_user_type == expected_detection.classification
        assert result_event.hostname == "myhostname"
        assert result_event.occurrence == expected_detection.occurrence
        assert result_event.frame_number == expected_detection.frame
        assert result_event.section_id == line_section.id
        assert result_event.event_type == EventType.SECTION_ENTER
        assert result_event.direction_vector.x1 == 0
        assert result_event.direction_vector.x2 == 0
        assert result_event.video_name == expected_detection.input_file_path.name

    @patch("OTAnalytics.domain.intersect.Intersector._select_coordinate_in_detection")
    def test_track_line_intersects_section_offset_applied(
        self,
        mock_select_coordinate_in_detection: Mock,
        track: Track,
    ) -> None:
        # Setup mock intersection implementation
        intersect_implementation = Mock()
        line_section = Mock()
        intersector = IntersectBySmallTrackComponents(
            intersect_implementation, line_section
        )

        mock_select_coordinate_in_detection.side_effect = [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(2, 0),
            Coordinate(3, 0),
            Coordinate(4, 1),
        ]

        mock_line_section = Mock()
        offset = RelativeOffsetCoordinate(1, 1)
        intersector._track_line_intersects_section(track, mock_line_section, offset)

        assert mock_select_coordinate_in_detection.call_count == 5


class TestIntersectAreaByTrackPoints:
    @pytest.fixture
    def area(self) -> Area:
        return Area(
            id=SectionId("N"),
            coordinates=[
                Coordinate(1, 1),
                Coordinate(1, 2),
                Coordinate(2, 2),
                Coordinate(2, 1),
                Coordinate(1, 1),
            ],
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0),
                EventType.SECTION_LEAVE: RelativeOffsetCoordinate(0, 0),
            },
            plugin_data={},
        )

    def test_intersect_track_starts_outside_section(
        self,
        area: Area,
        detection: Detection,
        track_builder: TrackBuilder,
        event_builder: EventBuilder,
    ) -> None:
        mock_implementation = Mock()
        mock_implementation.are_coordinates_within_polygon.return_value = [
            False,
            True,
            False,
        ]

        track_builder.add_xy_bbox(0.5, 1.5)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.5, 1.5)
        track_builder.add_frame(2)
        track_builder.add_microsecond(1)
        track_builder.append_detection()

        track_builder.add_xy_bbox(3, 1.5)
        track_builder.add_frame(3)
        track_builder.add_microsecond(2)
        track_builder.append_detection()

        track_builder.add_xy_bbox(3.5, 1.5)
        track_builder.add_frame(4)
        track_builder.add_microsecond(3)
        track_builder.append_detection()

        track_builder.add_xy_bbox(4, 1.5)
        track_builder.add_frame(5)
        track_builder.add_microsecond(4)
        track_builder.append_detection()
        track = track_builder.build_track()

        section_event_builder = SectionEventBuilder()
        section_event_builder.add_section_id(area.id)
        section_event_builder.add_direction_vector(detection, detection)

        intersector = IntersectAreaByTrackPoints(mock_implementation, area)
        result_events = intersector.intersect(track, section_event_builder)

        event_builder.add_microsecond(1)
        event_builder.add_frame_number(2)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        event_builder.append_section_event()

        event_builder.add_microsecond(2)
        event_builder.add_frame_number(3)
        event_builder.add_event_coordinate(3, 1.5)
        event_builder.add_event_type("section-leave")
        event_builder.append_section_event()
        expected_events = event_builder.build_events()
        assert result_events == expected_events

    def test_intersect_track_starts_inside_section(
        self,
        area: Area,
        detection: Detection,
        track_builder: TrackBuilder,
        event_builder: EventBuilder,
    ) -> None:
        mock_implementation = Mock()
        mock_implementation.are_coordinates_within_polygon.return_value = [
            True,
            False,
        ]

        track_builder.add_xy_bbox(1.5, 1.5)
        track_builder.add_frame(1)
        track_builder.add_microsecond(1)
        track_builder.append_detection()

        track_builder.add_xy_bbox(3, 1.5)
        track_builder.add_frame(2)
        track_builder.add_microsecond(2)
        track_builder.append_detection()

        track_builder.add_xy_bbox(3.5, 1.5)
        track_builder.add_frame(3)
        track_builder.add_microsecond(3)
        track_builder.append_detection()

        track_builder.add_xy_bbox(4, 1.5)
        track_builder.add_frame(4)
        track_builder.add_microsecond(4)
        track_builder.append_detection()

        track_builder.add_xy_bbox(4.5, 1.5)
        track_builder.add_frame(5)
        track_builder.add_microsecond(5)
        track_builder.append_detection()

        track = track_builder.build_track()

        section_event_builder = SectionEventBuilder()
        section_event_builder.add_section_id(area.id)
        section_event_builder.add_direction_vector(detection, detection)

        intersector = IntersectAreaByTrackPoints(mock_implementation, area)
        result_events = intersector.intersect(track, section_event_builder)

        event_builder.add_microsecond(1)
        event_builder.add_frame_number(1)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        event_builder.append_section_event()

        event_builder.add_microsecond(2)
        event_builder.add_frame_number(2)
        event_builder.add_event_coordinate(3, 1.5)
        event_builder.add_event_type("section-leave")
        event_builder.append_section_event()

        expected_events = event_builder.build_events()

        assert result_events == expected_events

    def test_intersect_track_is_inside_section(
        self,
        area: Area,
        detection: Detection,
        track_builder: TrackBuilder,
        event_builder: EventBuilder,
    ) -> None:
        mock_implementation = Mock()
        mock_implementation.are_coordinates_within_polygon.return_value = [
            True,
        ]

        track_builder.add_xy_bbox(1.5, 1.5)
        track_builder.add_frame(1)
        track_builder.add_microsecond(1)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.7, 1.5)
        track_builder.add_frame(2)
        track_builder.add_microsecond(2)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.8, 1.5)
        track_builder.add_frame(3)
        track_builder.add_microsecond(3)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.7, 1.5)
        track_builder.add_frame(4)
        track_builder.add_microsecond(4)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.8, 1.5)
        track_builder.add_frame(5)
        track_builder.add_microsecond(4)
        track_builder.append_detection()

        track = track_builder.build_track()

        section_event_builder = SectionEventBuilder()
        section_event_builder.add_section_id(area.id)
        section_event_builder.add_direction_vector(detection, detection)

        intersector = IntersectAreaByTrackPoints(mock_implementation, area)
        result_events = intersector.intersect(track, section_event_builder)

        event_builder.add_microsecond(1)
        event_builder.add_frame_number(1)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        event_builder.append_section_event()
        expected_events = event_builder.build_events()

        assert result_events == expected_events

    def test_intersect_track_starts_outside_and_stays_inside_section(
        self, area: Area, detection: Detection, track_builder: TrackBuilder
    ) -> None:
        mock_implementation = Mock()
        mock_implementation.are_coordinates_within_polygon.return_value = [False, True]
        track_builder.add_xy_bbox(0.5, 1.5)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.5, 1.5)
        track_builder.add_frame(2)
        track_builder.add_microsecond(1)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.7, 1.5)
        track_builder.add_frame(3)
        track_builder.add_microsecond(2)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.8, 1.5)
        track_builder.add_frame(4)
        track_builder.add_microsecond(3)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.7, 1.5)
        track_builder.add_frame(5)
        track_builder.add_microsecond(4)
        track_builder.append_detection()

        track = track_builder.build_track()

        event_builder = SectionEventBuilder()
        event_builder.add_section_id(area.id)
        event_builder.add_direction_vector(detection, detection)

        intersector = IntersectAreaByTrackPoints(mock_implementation, area)
        result_events = intersector.intersect(track, event_builder)
        expected_events = [
            Event(
                road_user_id=1,
                road_user_type="car",
                hostname="myhostname",
                occurrence=datetime(2020, 1, 1, 0, 0, 0, 1),
                frame_number=2,
                section_id=SectionId("N"),
                event_coordinate=ImageCoordinate(1.5, 1.5),
                event_type=EventType.SECTION_ENTER,
                direction_vector=DirectionVector2D(0, 0),
                video_name="myhostname_file.otdet",
            )
        ]
        assert result_events == expected_events

    def test_intersect_track_starts_outside_section_with_multiple_intersections(
        self,
        area: Area,
        detection: Detection,
        track_builder: TrackBuilder,
        event_builder: EventBuilder,
    ) -> None:
        mock_implementation = Mock()
        mock_implementation.are_coordinates_within_polygon.return_value = [
            False,
            True,
            False,
            True,
            False,
        ]

        track_builder.add_xy_bbox(0.5, 1.5)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.5, 1.5)
        track_builder.add_frame(2)
        track_builder.occurrence_microsecond = 1
        track_builder.append_detection()

        track_builder.add_xy_bbox(3, 1.5)
        track_builder.add_frame(3)
        track_builder.occurrence_microsecond = 2
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.5, 1.5)
        track_builder.add_frame(4)
        track_builder.occurrence_microsecond = 3
        track_builder.append_detection()

        track_builder.add_xy_bbox(3, 1.5)
        track_builder.add_frame(5)
        track_builder.occurrence_microsecond = 4
        track_builder.append_detection()

        track = track_builder.build_track()

        section_event_builder = SectionEventBuilder()
        section_event_builder.add_section_id(area.id)
        section_event_builder.add_direction_vector(detection, detection)

        intersector = IntersectAreaByTrackPoints(mock_implementation, area)
        result_events = intersector.intersect(track, section_event_builder)

        event_builder.add_microsecond(1)
        event_builder.add_frame_number(2)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        event_builder.append_section_event()

        event_builder.add_microsecond(2)
        event_builder.add_frame_number(3)
        event_builder.add_event_coordinate(3, 1.5)
        event_builder.add_event_type("section-leave")
        event_builder.append_section_event()

        event_builder.add_microsecond(3)
        event_builder.add_frame_number(4)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        event_builder.append_section_event()

        event_builder.add_microsecond(4)
        event_builder.add_frame_number(5)
        event_builder.add_event_coordinate(3, 1.5)
        event_builder.add_event_type("section-leave")
        event_builder.append_section_event()

        expected_events = event_builder.build_events()

        assert result_events == expected_events

    def test_intersect_track_starts_inside_section_with_multiple_intersections(
        self,
        area: Area,
        detection: Detection,
        track_builder: TrackBuilder,
        event_builder: EventBuilder,
    ) -> None:
        mock_implementation = Mock()
        mock_implementation.are_coordinates_within_polygon.return_value = [
            True,
            False,
            True,
            False,
        ]

        track_builder.add_xy_bbox(1.5, 1.5)
        track_builder.add_frame(2)
        track_builder.add_microsecond(1)
        track_builder.append_detection()

        track_builder.add_xy_bbox(3, 1.5)
        track_builder.add_frame(3)
        track_builder.add_microsecond(2)
        track_builder.append_detection()

        track_builder.add_xy_bbox(1.5, 1.5)
        track_builder.add_frame(4)
        track_builder.add_microsecond(3)
        track_builder.append_detection()

        track_builder.add_xy_bbox(3, 1.5)
        track_builder.add_frame(5)
        track_builder.add_microsecond(4)
        track_builder.append_detection()

        track_builder.add_xy_bbox(4, 1.5)
        track_builder.add_frame(6)
        track_builder.add_microsecond(5)
        track_builder.append_detection()

        track = track_builder.build_track()

        section_event_builder = SectionEventBuilder()
        section_event_builder.add_section_id(area.id)
        section_event_builder.add_direction_vector(detection, detection)

        intersector = IntersectAreaByTrackPoints(mock_implementation, area)
        result_events = intersector.intersect(track, section_event_builder)

        event_builder.add_microsecond(1)
        event_builder.add_frame_number(2)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        event_builder.append_section_event()

        event_builder.add_microsecond(2)
        event_builder.add_frame_number(3)
        event_builder.add_event_coordinate(3, 1.5)
        event_builder.add_event_type("section-leave")
        event_builder.append_section_event()

        event_builder.add_microsecond(3)
        event_builder.add_frame_number(4)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        event_builder.append_section_event()

        event_builder.add_microsecond(4)
        event_builder.add_frame_number(5)
        event_builder.add_event_coordinate(3, 1.5)
        event_builder.add_event_type("section-leave")
        event_builder.append_section_event()

        expected_events = event_builder.build_events()

        assert result_events == expected_events

    @staticmethod
    def compare_events(first: Event, second: Event) -> None:
        assert first.road_user_id == second.road_user_id
        assert first.road_user_type == second.road_user_type
        assert first.hostname == second.hostname
        assert first.frame_number == second.frame_number
        assert first.section_id == second.section_id
        assert first.event_coordinate.x == second.event_coordinate.x
        assert first.event_coordinate.y == second.event_coordinate.y
        assert first.event_coordinate == second.event_coordinate
        assert first.event_type == second.event_type
        assert first.direction_vector == second.direction_vector
        assert first.video_name == second.video_name
