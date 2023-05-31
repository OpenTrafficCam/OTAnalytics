from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from OTAnalytics.application.eventlist import SceneActionDetector, SectionActionDetector
from OTAnalytics.domain.event import (
    Event,
    EventType,
    SceneEventBuilder,
    SectionEventBuilder,
)
from OTAnalytics.domain.geometry import (
    Coordinate,
    DirectionVector2D,
    ImageCoordinate,
    RelativeOffsetCoordinate,
)
from OTAnalytics.domain.intersect import Intersector
from OTAnalytics.domain.section import LineSection, SectionId
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


@pytest.fixture
def line_section() -> LineSection:
    return LineSection(
        id=SectionId("N"),
        name="N",
        relative_offset_coordinates={
            EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
        },
        plugin_data={},
        coordinates=[Coordinate(5, 0), Coordinate(5, 10)],
    )


class TestSectionActionDetector:
    def test_detect_action(self, line_section: LineSection, track: Track) -> None:
        mock_intersector = Mock(spec=Intersector)
        mock_section_event_builder = Mock(spec=SectionEventBuilder)
        mock_event = Mock(spec=Event)

        mock_intersector.intersect.return_value = mock_event

        section_action_detector = SectionActionDetector(
            mock_intersector, mock_section_event_builder
        )
        result_event = section_action_detector._detect(line_section, track)

        mock_section_event_builder.add_section_id.assert_called()
        mock_section_event_builder.add_event_type.assert_called()
        mock_intersector.intersect.assert_called()
        assert mock_event == result_event

    def test_detect_actions(self, line_section: LineSection, track: Track) -> None:
        mock_intersector = Mock(spec=Intersector)
        mock_section_event_builder = Mock(spec=SectionEventBuilder)
        mock_event = Mock(spec=Event)

        mock_intersector.intersect.return_value = [mock_event]

        section_action_detector = SectionActionDetector(
            mock_intersector, mock_section_event_builder
        )

        result_events = section_action_detector.detect([line_section], [track])
        assert result_events == [mock_event]


class TestSceneActionDetector:
    def test_detect_enter_scene(self, track: Track) -> None:
        scene_event_builder = SceneEventBuilder()
        scene_event_builder.add_event_type(EventType.ENTER_SCENE)
        scene_event_builder.add_road_user_type("car")
        scene_action_detector = SceneActionDetector(scene_event_builder)
        event = scene_action_detector.detect_enter_scene(track)
        assert event == Event(
            road_user_id=1,
            road_user_type="car",
            hostname="myhostname",
            occurrence=datetime(2022, 1, 1, 0, 0, 0, 0),
            frame_number=1,
            section_id=None,
            event_coordinate=ImageCoordinate(0.0, 5.0),
            event_type=EventType.ENTER_SCENE,
            direction_vector=DirectionVector2D(10, 0),
            video_name="myhostname_something.otdet",
        )

    def test_detect_leave_scene(self, track: Track) -> None:
        scene_event_builder = SceneEventBuilder()
        scene_event_builder.add_event_type(EventType.LEAVE_SCENE)
        scene_event_builder.add_road_user_type("car")
        scene_action_detector = SceneActionDetector(scene_event_builder)
        event = scene_action_detector.detect_leave_scene(track)
        assert event == Event(
            road_user_id=1,
            road_user_type="car",
            hostname="myhostname",
            occurrence=datetime(2022, 1, 1, 0, 0, 0, 4),
            frame_number=5,
            section_id=None,
            event_coordinate=ImageCoordinate(25, 5),
            event_type=EventType.LEAVE_SCENE,
            direction_vector=DirectionVector2D(5, 0),
            video_name="myhostname_something.otdet",
        )

    @patch.object(SceneActionDetector, "detect_leave_scene")
    @patch.object(SceneActionDetector, "detect_enter_scene")
    def test_detect(
        self, mock_detect_enter_scene: Mock, mock_detect_leave_scene: Mock
    ) -> None:
        mock_track_1 = Mock(spec=Track)
        mock_track_2 = Mock(spec=Track)
        mock_tracks = [mock_track_1, mock_track_2]
        mock_event_builder = Mock(spec=SceneEventBuilder)

        scene_action_detector = SceneActionDetector(mock_event_builder)
        scene_action_detector.detect(mock_tracks)

        mock_detect_enter_scene.assert_any_call(mock_track_1)
        mock_detect_leave_scene.assert_any_call(mock_track_1)
        mock_detect_enter_scene.assert_any_call(mock_track_2)
        mock_detect_leave_scene.assert_any_call(mock_track_2)

        assert mock_detect_enter_scene.call_count == 2
        assert mock_detect_leave_scene.call_count == 2
