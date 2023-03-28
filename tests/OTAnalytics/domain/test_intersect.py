from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.domain.event import EventType, SectionEventBuilder
from OTAnalytics.domain.geometry import Coordinate, Line
from OTAnalytics.domain.intersect import (
    IntersectBySmallTrackComponents,
    IntersectBySplittingTrackLine,
    IntersectImplementation,
)
from OTAnalytics.domain.section import LineSection
from OTAnalytics.domain.track import Detection, Track, TrackId


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

    return Track(track_id, "car", [detection_1, detection_2])


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
        event_builder.add_section_id("N")
        event_builder.add_event_type(EventType.SECTION_ENTER)
        event_builder.add_direction_vector(detection, detection)

        line_section = LineSection(
            id="N", start=Coordinate(5, 0), end=Coordinate(5, 10)
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
        intersection_result: list[Line] = [
            Line([Coordinate(0, 5), Coordinate(5, 5)]),
            Line([Coordinate(5, 5), Coordinate(10, 5)]),
        ]
        mock_implementation.split_line_with_line.return_value = intersection_result

        # Setup event builder
        event_builder = SectionEventBuilder()
        event_builder.add_section_id("N")
        event_builder.add_event_type(EventType.SECTION_ENTER)
        event_builder.add_direction_vector(detection, detection)

        line_section = LineSection(
            id="N", start=Coordinate(5, 0), end=Coordinate(5, 10)
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
