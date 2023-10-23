from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.domain.event import Event, EventType, SceneEventBuilder
from OTAnalytics.domain.geometry import (
    Coordinate,
    DirectionVector2D,
    ImageCoordinate,
    RelativeOffsetCoordinate,
)
from OTAnalytics.domain.section import LineSection, SectionId
from OTAnalytics.domain.track import (
    Detection,
    PythonDetection,
    PythonTrack,
    Track,
    TrackId,
)


@pytest.fixture
def detection() -> Detection:
    return PythonDetection(
        _classification="car",
        _confidence=0.5,
        _x=0.0,
        _y=5.0,
        _w=15.3,
        _h=30.5,
        _frame=1,
        _occurrence=datetime(2022, 1, 1, 0, 0, 0, 0),
        _interpolated_detection=False,
        _track_id=TrackId("1"),
        _video_name="myhostname_something.mp4",
    )


@pytest.fixture
def track() -> Track:
    track_id = TrackId("1")

    detection_1 = PythonDetection(
        _classification="car",
        _confidence=0.5,
        _x=0.0,
        _y=5.0,
        _w=15.3,
        _h=30.5,
        _frame=1,
        _occurrence=datetime(2022, 1, 1, 0, 0, 0, 0),
        _interpolated_detection=False,
        _track_id=TrackId("1"),
        _video_name="myhostname_something.mp4",
    )
    detection_2 = PythonDetection(
        _classification="car",
        _confidence=0.5,
        _x=10.0,
        _y=5.0,
        _w=15.3,
        _h=30.5,
        _frame=2,
        _occurrence=datetime(2022, 1, 1, 0, 0, 0, 1),
        _interpolated_detection=False,
        _track_id=TrackId("1"),
        _video_name="myhostname_something.mp4",
    )
    detection_3 = PythonDetection(
        _classification="car",
        _confidence=0.5,
        _x=15.0,
        _y=5.0,
        _w=15.3,
        _h=30.5,
        _frame=3,
        _occurrence=datetime(2022, 1, 1, 0, 0, 0, 2),
        _interpolated_detection=False,
        _track_id=TrackId("1"),
        _video_name="myhostname_something.mp4",
    )
    detection_4 = PythonDetection(
        _classification="car",
        _confidence=0.5,
        _x=20.0,
        _y=5.0,
        _w=15.3,
        _h=30.5,
        _frame=4,
        _occurrence=datetime(2022, 1, 1, 0, 0, 0, 3),
        _interpolated_detection=False,
        _track_id=TrackId("1"),
        _video_name="myhostname_something.mp4",
    )
    detection_5 = PythonDetection(
        _classification="car",
        _confidence=0.5,
        _x=25.0,
        _y=5.0,
        _w=15.3,
        _h=30.5,
        _frame=5,
        _occurrence=datetime(2022, 1, 1, 0, 0, 0, 4),
        _interpolated_detection=False,
        _track_id=TrackId("1"),
        _video_name="myhostname_something.mp4",
    )

    return PythonTrack(
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


class TestSceneActionDetector:
    def test_detect_enter_scene(self, track: Track) -> None:
        scene_event_builder = SceneEventBuilder()
        scene_event_builder.add_event_type(EventType.ENTER_SCENE)
        scene_event_builder.add_road_user_type("car")
        scene_action_detector = SceneActionDetector(scene_event_builder)
        event = scene_action_detector.detect_enter_scene(track)
        assert event == Event(
            road_user_id="1",
            road_user_type="car",
            hostname="myhostname",
            occurrence=datetime(2022, 1, 1, 0, 0, 0, 0),
            frame_number=1,
            section_id=None,
            event_coordinate=ImageCoordinate(0.0, 5.0),
            event_type=EventType.ENTER_SCENE,
            direction_vector=DirectionVector2D(10, 0),
            video_name="myhostname_something.mp4",
        )

    def test_detect_leave_scene(self, track: Track) -> None:
        scene_event_builder = SceneEventBuilder()
        scene_event_builder.add_event_type(EventType.LEAVE_SCENE)
        scene_event_builder.add_road_user_type("car")
        scene_action_detector = SceneActionDetector(scene_event_builder)
        event = scene_action_detector.detect_leave_scene(track)
        assert event == Event(
            road_user_id="1",
            road_user_type="car",
            hostname="myhostname",
            occurrence=datetime(2022, 1, 1, 0, 0, 0, 4),
            frame_number=5,
            section_id=None,
            event_coordinate=ImageCoordinate(25, 5),
            event_type=EventType.LEAVE_SCENE,
            direction_vector=DirectionVector2D(5, 0),
            video_name="myhostname_something.mp4",
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
