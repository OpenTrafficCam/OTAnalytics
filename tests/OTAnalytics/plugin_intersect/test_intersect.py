from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from OTAnalytics.application.geometry import (
    SectionGeometryBuilder,
    TrackGeometryBuilder,
)
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.event import Event, EventType, SectionEventBuilder
from OTAnalytics.domain.geometry import (
    Coordinate,
    DirectionVector2D,
    ImageCoordinate,
    Line,
    RelativeOffsetCoordinate,
)
from OTAnalytics.domain.intersect import IntersectImplementation
from OTAnalytics.domain.section import Area, LineSection, Section, SectionId
from OTAnalytics.domain.track import Track
from OTAnalytics.plugin_intersect.simple_intersect import (
    SimpleIntersectAreaByTrackPoints,
    SimpleIntersectBySmallestTrackSegments,
    SimpleIntersectBySplittingTrackLine,
    SimpleTracksIntersectingSections,
)
from tests.conftest import EventBuilder, TrackBuilder


@pytest.fixture
def track(track_builder: TrackBuilder) -> Track:
    classification = "car"
    track_id = 1

    track_builder.add_track_class(classification)
    track_builder.add_detection_class(classification)
    track_builder.add_track_id(track_id)
    track_builder.add_wh_bbox(15.3, 30.5)

    track_builder.add_frame(1)
    track_builder.add_second(0)
    track_builder.add_xy_bbox(0.0, 5.0)
    track_builder.append_detection()

    track_builder.add_frame(2)
    track_builder.add_second(1)
    track_builder.add_xy_bbox(10.0, 5.0)
    track_builder.append_detection()

    track_builder.add_frame(3)
    track_builder.add_second(2)
    track_builder.add_xy_bbox(15.0, 5.0)
    track_builder.append_detection()

    track_builder.add_frame(5)
    track_builder.add_second(3)
    track_builder.add_xy_bbox(20.0, 5.0)
    track_builder.append_detection()

    track_builder.add_frame(5)
    track_builder.add_second(4)
    track_builder.add_xy_bbox(25.0, 5.0)
    track_builder.append_detection()
    return track_builder.build_track()


@pytest.fixture
def closed_track(track_builder: TrackBuilder) -> Track:
    classification = "car"
    track_id = 2

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
    track: Track, event_builder: EventBuilder
) -> tuple[Track, LineSection, list[Event]]:
    section = LineSection(
        id=SectionId("N"),
        name="N",
        relative_offset_coordinates={
            EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
        },
        plugin_data={},
        coordinates=[Coordinate(5, 0), Coordinate(5, 10)],
    )

    event_builder.add_road_user_id(track.id.id)
    event_builder.add_road_user_type(track.classification)
    event_builder.add_section_id(section.id.id)
    event_builder.add_event_type(EventType.SECTION_ENTER.value)

    event_builder.add_frame_number(2)
    event_builder.add_second(1)
    event_builder.add_direction_vector(10, 0)
    event_builder.add_event_coordinate(10.0, 5.0)
    event_builder.append_section_event()

    expected_events = event_builder.build_events()
    return (track, section, expected_events)


@pytest.fixture
def test_case_closed_track_line_section(
    closed_track: Track, event_builder: EventBuilder
) -> tuple[Track, LineSection, list[Event]]:
    section = LineSection(
        id=SectionId("N"),
        name="N",
        relative_offset_coordinates={
            EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
        },
        plugin_data={},
        coordinates=[Coordinate(0, 1.5), Coordinate(3, 1.5)],
    )

    event_builder.add_road_user_id(closed_track.id.id)
    event_builder.add_road_user_type(closed_track.classification)
    event_builder.add_section_id(section.id.id)
    event_builder.add_event_type(EventType.SECTION_ENTER.value)

    event_builder.add_second(3)
    event_builder.add_frame_number(3)
    event_builder.add_direction_vector(0, 1)
    event_builder.add_event_coordinate(2, 2)
    event_builder.append_section_event()

    event_builder.add_second(5)
    event_builder.add_frame_number(5)
    event_builder.add_direction_vector(0, -1)
    event_builder.add_event_coordinate(1, 1)
    event_builder.append_section_event()

    expected_events = event_builder.build_events()
    return (closed_track, section, expected_events)


class TestIntersectBySplittingTrackLine:
    def test_intersect(self, track: Track) -> None:
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

        line_section = LineSection(
            id=SectionId("N"),
            name="N",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            coordinates=[Coordinate(5, 0), Coordinate(5, 10)],
        )

        intersector = SimpleIntersectBySplittingTrackLine(
            mock_implementation, line_section
        )
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
        assert result_event.direction_vector.x1 == 10
        assert result_event.direction_vector.x2 == 0
        assert result_event.video_name == expected_detection.input_file_path.name

    def test_intersect_track_offset_applied_to_event_coordinate(
        self, track: Track
    ) -> None:
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

        line_section = LineSection(
            id=SectionId("N"),
            name="N",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(1, 1)
            },
            plugin_data={},
            coordinates=[Coordinate(5, 0), Coordinate(5, 10)],
        )

        intersector = SimpleIntersectBySplittingTrackLine(
            mock_implementation, line_section
        )
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
        assert result_event.direction_vector.x1 == 10
        assert result_event.direction_vector.x2 == 0
        assert result_event.video_name == expected_detection.input_file_path.name
        assert result_event.event_coordinate == ImageCoordinate(25.3, 35.5)


class TestIntersectBySmallTrackComponents:
    @pytest.mark.parametrize(
        "test_case,intersect_side_effect",
        [
            (
                "test_case_track_line_section",
                [True, True, False, False, False, False, False],
            ),
            ("test_case_closed_track_line_section", [True, False, True, False, True]),
        ],
    )
    def test_intersect(
        self,
        test_case: str,
        intersect_side_effect: list[bool],
        request: pytest.FixtureRequest,
    ) -> None:
        track: Track
        expected_events: list[Event]
        track, section, expected_events = request.getfixturevalue(test_case)

        # Setup mock intersection implementation
        mock_implementation = Mock(spec=IntersectImplementation)
        mock_implementation.line_intersects_line.side_effect = intersect_side_effect

        # Setup event builder
        section_event_builder = SectionEventBuilder()
        section_event_builder.add_section_id(SectionId("N"))
        section_event_builder.add_event_type(EventType.SECTION_ENTER)

        line_section = LineSection(
            id=SectionId("N"),
            name="N",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            coordinates=[Coordinate(5, 0), Coordinate(5, 10)],
        )

        intersector = SimpleIntersectBySmallestTrackSegments(
            mock_implementation, line_section
        )
        result_events = intersector.intersect(track, section_event_builder)
        assert result_events == expected_events

    def test_intersect_track_offset_applied_to_event_coordinate(
        self, track: Track
    ) -> None:
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

        line_section = LineSection(
            id=SectionId("N"),
            name="N",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(1, 1)
            },
            plugin_data={},
            coordinates=[Coordinate(5, 0), Coordinate(5, 10)],
        )

        intersector = SimpleIntersectBySmallestTrackSegments(
            mock_implementation, line_section
        )
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
        assert result_event.direction_vector.x1 == 10
        assert result_event.direction_vector.x2 == 0
        assert result_event.video_name == expected_detection.input_file_path.name
        assert result_event.event_coordinate == ImageCoordinate(25.3, 35.5)

    @patch("OTAnalytics.domain.intersect.Intersector._select_coordinate_in_detection")
    def test_track_line_intersects_section_offset_applied(
        self,
        mock_select_coordinate_in_detection: Mock,
        track: Track,
    ) -> None:
        # Setup mock intersection implementation
        intersect_implementation = Mock()
        line_section = Mock()
        intersector = SimpleIntersectBySmallestTrackSegments(
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
            name="N",
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
        track_builder: TrackBuilder,
        event_builder: EventBuilder,
    ) -> None:
        mock_implementation = Mock()
        mock_implementation.are_coordinates_within_polygon.return_value = [
            False,
            True,
            False,
            False,
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

        intersector = SimpleIntersectAreaByTrackPoints(mock_implementation, area)
        result_events = intersector.intersect(track, section_event_builder)

        event_builder.add_microsecond(1)
        event_builder.add_frame_number(2)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        event_builder.add_direction_vector(1, 0)
        event_builder.append_section_event()

        event_builder.add_microsecond(2)
        event_builder.add_frame_number(3)
        event_builder.add_event_coordinate(3, 1.5)
        event_builder.add_event_type("section-leave")
        event_builder.add_direction_vector(1.5, 0)
        event_builder.append_section_event()
        expected_events = event_builder.build_events()
        assert result_events == expected_events

    def test_intersect_track_starts_inside_section(
        self,
        area: Area,
        track_builder: TrackBuilder,
        event_builder: EventBuilder,
    ) -> None:
        mock_implementation = Mock()
        mock_implementation.are_coordinates_within_polygon.return_value = [
            True,
            False,
            False,
            False,
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

        intersector = SimpleIntersectAreaByTrackPoints(mock_implementation, area)
        result_events = intersector.intersect(track, section_event_builder)

        event_builder.add_microsecond(1)
        event_builder.add_frame_number(1)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        event_builder.add_direction_vector(1.5, 0)
        event_builder.append_section_event()

        event_builder.add_microsecond(2)
        event_builder.add_frame_number(2)
        event_builder.add_event_coordinate(3, 1.5)
        event_builder.add_event_type("section-leave")
        event_builder.add_direction_vector(1.5, 0)
        event_builder.append_section_event()

        expected_events = event_builder.build_events()

        assert result_events == expected_events

    def test_intersect_track_is_inside_section(
        self,
        area: Area,
        track_builder: TrackBuilder,
        event_builder: EventBuilder,
    ) -> None:
        mock_implementation = Mock()
        mock_implementation.are_coordinates_within_polygon.return_value = [
            True,
            True,
            True,
            True,
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

        intersector = SimpleIntersectAreaByTrackPoints(mock_implementation, area)
        result_events = intersector.intersect(track, section_event_builder)

        event_builder.add_microsecond(1)
        event_builder.add_frame_number(1)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        # 1.7 - 1.5 != 0.2 but 0.19999999999999996 due to FP precision error
        event_builder.add_direction_vector(1.7 - 1.5, 1.5 - 1.5)
        event_builder.append_section_event()
        expected_events = event_builder.build_events()

        assert result_events == expected_events

    def test_intersect_track_starts_outside_and_stays_inside_section(
        self, area: Area, track_builder: TrackBuilder
    ) -> None:
        mock_implementation = Mock()
        mock_implementation.are_coordinates_within_polygon.return_value = [
            False,
            True,
            True,
            True,
            True,
        ]
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

        intersector = SimpleIntersectAreaByTrackPoints(mock_implementation, area)
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
                direction_vector=DirectionVector2D(1, 0),
                video_name="myhostname_file.mp4",
            )
        ]
        assert result_events == expected_events

    def test_intersect_track_starts_outside_section_with_multiple_intersections(
        self,
        area: Area,
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

        intersector = SimpleIntersectAreaByTrackPoints(mock_implementation, area)
        result_events = intersector.intersect(track, section_event_builder)

        event_builder.add_microsecond(1)
        event_builder.add_frame_number(2)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        event_builder.add_direction_vector(1, 0)
        event_builder.append_section_event()

        event_builder.add_microsecond(2)
        event_builder.add_frame_number(3)
        event_builder.add_event_coordinate(3, 1.5)
        event_builder.add_event_type("section-leave")
        event_builder.add_direction_vector(1.5, 0)
        event_builder.append_section_event()

        event_builder.add_microsecond(3)
        event_builder.add_frame_number(4)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        event_builder.add_direction_vector(-1.5, 0)
        event_builder.append_section_event()

        event_builder.add_microsecond(4)
        event_builder.add_frame_number(5)
        event_builder.add_event_coordinate(3, 1.5)
        event_builder.add_event_type("section-leave")
        event_builder.add_direction_vector(1.5, 0)
        event_builder.append_section_event()

        expected_events = event_builder.build_events()

        assert result_events == expected_events

    def test_intersect_track_starts_inside_section_with_multiple_intersections(
        self,
        area: Area,
        track_builder: TrackBuilder,
        event_builder: EventBuilder,
    ) -> None:
        mock_implementation = Mock()
        mock_implementation.are_coordinates_within_polygon.return_value = [
            True,
            False,
            True,
            False,
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

        intersector = SimpleIntersectAreaByTrackPoints(mock_implementation, area)
        result_events = intersector.intersect(track, section_event_builder)

        event_builder.add_microsecond(1)
        event_builder.add_frame_number(2)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        event_builder.add_direction_vector(1.5, 0)
        event_builder.append_section_event()

        event_builder.add_microsecond(2)
        event_builder.add_frame_number(3)
        event_builder.add_event_coordinate(3, 1.5)
        event_builder.add_event_type("section-leave")
        event_builder.add_direction_vector(1.5, 0)
        event_builder.append_section_event()

        event_builder.add_microsecond(3)
        event_builder.add_frame_number(4)
        event_builder.add_event_coordinate(1.5, 1.5)
        event_builder.add_event_type("section-enter")
        event_builder.add_direction_vector(-1.5, 0)
        event_builder.append_section_event()

        event_builder.add_microsecond(4)
        event_builder.add_frame_number(5)
        event_builder.add_event_coordinate(3, 1.5)
        event_builder.add_event_type("section-leave")
        event_builder.add_direction_vector(1.5, 0)
        event_builder.append_section_event()

        expected_events = event_builder.build_events()

        assert result_events == expected_events

    def test_intersect_track_offset_applied_to_event_coordinate(
        self,
        track_builder: TrackBuilder,
        event_builder: EventBuilder,
    ) -> None:
        mock_implementation = Mock()
        mock_implementation.are_coordinates_within_polygon.return_value = [
            False,
            True,
            False,
            False,
            False,
        ]
        mock_coordinate = Mock()
        area = Area(
            id=SectionId("N"),
            name="N",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(1, 1),
                EventType.SECTION_LEAVE: RelativeOffsetCoordinate(1, 1),
            },
            plugin_data={},
            coordinates=[
                mock_coordinate,
                mock_coordinate,
                mock_coordinate,
                mock_coordinate,
            ],
        )

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

        intersector = SimpleIntersectAreaByTrackPoints(mock_implementation, area)
        result_events = intersector.intersect(track, section_event_builder)

        event_builder.add_microsecond(1)
        event_builder.add_frame_number(2)
        event_builder.add_event_coordinate(11.5, 11.5)
        event_builder.add_direction_vector(1, 0)
        event_builder.add_event_type("section-enter")
        event_builder.append_section_event()

        event_builder.add_microsecond(2)
        event_builder.add_frame_number(3)
        event_builder.add_direction_vector(1.5, 0)
        event_builder.add_event_coordinate(13, 11.5)
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

    def test_intersect_closed_track(
        self, closed_track: Track, event_builder: EventBuilder
    ) -> None:
        mock_implementation = Mock()
        mock_implementation.are_coordinates_within_polygon.return_value = [
            False,
            False,
            True,
            True,
            False,
        ]
        area = Area(
            id=SectionId("N"),
            name="N",
            coordinates=[
                Coordinate(0, 1.5),
                Coordinate(3, 1.5),
                Coordinate(3, 2.5),
                Coordinate(0, 2.5),
                Coordinate(0, 1.5),
            ],
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0),
                EventType.SECTION_LEAVE: RelativeOffsetCoordinate(0, 0),
            },
            plugin_data={},
        )

        section_event_builder = SectionEventBuilder()
        section_event_builder.add_section_id(area.id)

        intersector = SimpleIntersectAreaByTrackPoints(mock_implementation, area)
        result_events = intersector.intersect(closed_track, section_event_builder)

        event_builder.add_road_user_id(closed_track.id.id)
        event_builder.add_second(3)
        event_builder.add_frame_number(3)
        event_builder.add_event_coordinate(2, 2)
        event_builder.add_event_type("section-enter")
        event_builder.add_direction_vector(0, 1)
        event_builder.append_section_event()

        event_builder.add_second(5)
        event_builder.add_frame_number(5)
        event_builder.add_event_coordinate(1, 1)
        event_builder.add_event_type("section-leave")
        event_builder.add_direction_vector(0, -1)
        event_builder.append_section_event()
        expected_events = event_builder.build_events()
        assert result_events == expected_events


class TestSimpleTracksIntersectingSections:
    def test_tracks_intersecting_sections(self, track: Track) -> None:
        get_all_tracks = Mock(spec=GetAllTracks)
        get_all_tracks.return_value = [track]

        section = Mock(spec=Section)
        offset = RelativeOffsetCoordinate(0, 0)
        section.get_offset.return_value = offset

        intersect_implementation = Mock(spec=IntersectImplementation)
        intersect_implementation.line_intersects_line.return_value = True

        section_geom = Mock(spec=Line)
        track_geom = Mock(spec=Line)

        track_geometry_builder = Mock(spec=TrackGeometryBuilder)
        track_geometry_builder.build.return_value = track_geom
        section_geometry_builder = Mock(spec=SectionGeometryBuilder)
        section_geometry_builder.build_as_line.return_value = section_geom

        tracks_intersecting_sections = SimpleTracksIntersectingSections(
            get_all_tracks,
            intersect_implementation,
            track_geometry_builder,
            section_geometry_builder,
        )
        intersecting = tracks_intersecting_sections([section])

        assert intersecting == {track.id}
        get_all_tracks.assert_called_once()
        section.get_offset.assert_called_once_with(EventType.SECTION_ENTER)
        track_geometry_builder.build.assert_called_once_with(track, offset)
        section_geometry_builder.build_as_line.assert_called_once_with(section)
        intersect_implementation.line_intersects_line.assert_called_once_with(
            track_geom, section_geom
        )
