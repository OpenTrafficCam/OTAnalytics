from datetime import datetime
from unittest.mock import Mock

import pytest

from OTAnalytics.application.eventlist import SceneActionDetector, SceneEventListBuilder
from OTAnalytics.domain.event import Event, EventType
from OTAnalytics.domain.geometry import (
    Coordinate,
    ImageCoordinate,
    RelativeOffsetCoordinate,
    calculate_direction_vector,
)
from OTAnalytics.domain.section import LineSection, SectionId
from OTAnalytics.domain.track import (
    TRACK_CLASSIFICATION,
    TRACK_ID,
    Detection,
    Track,
    TrackId,
)
from OTAnalytics.domain.track_dataset.track_dataset import (
    END_FRAME,
    END_OCCURRENCE,
    END_VIDEO_NAME,
    END_X,
    END_Y,
    START_FRAME,
    START_OCCURRENCE,
    START_VIDEO_NAME,
    START_X,
    START_Y,
    TrackDataset,
    TrackSegmentDataset,
)
from OTAnalytics.plugin_datastore.python_track_store import PythonDetection, PythonTrack

HOSTNAME = "myhostname"


def create_detection(
    _classification: str = "car",
    _confidence: float = 0.5,
    _x: float = 0.0,
    _y: float = 5.0,
    _w: float = 15.3,
    _h: float = 30.5,
    _frame: int = 1,
    _occurrence: datetime = datetime(2022, 1, 1, 0, 0, 0, 0),
    _interpolated_detection: bool = False,
    _track_id: TrackId = TrackId("1"),
    _video_name: str = HOSTNAME + "_something.mp4",
    _input_file: str = HOSTNAME + "_something.ottrk",
) -> Detection:
    return PythonDetection(
        _classification=_classification,
        _confidence=_confidence,
        _x=_x,
        _y=_y,
        _w=_w,
        _h=_h,
        _frame=_frame,
        _occurrence=datetime(2022, 1, 1, 0, 0, 0, _frame - 1),
        _interpolated_detection=_interpolated_detection,
        _track_id=_track_id,
        _video_name=_video_name,
        _input_file=_input_file,
    )


@pytest.fixture
def detection() -> Detection:
    return create_detection(
        _classification="car",
        _confidence=0.5,
        _x=0.0,
        _y=5.0,
        _frame=1,
        _track_id=TrackId("1"),
    )


@pytest.fixture
def track() -> Track:
    return create_track(1)


@pytest.fixture
def track_2() -> Track:
    return create_track(2)


def create_track(track_number: int) -> Track:
    track_id = TrackId(f"{track_number}")
    y = 5.0 * track_number
    detection_1 = create_detection(
        _x=0.0,
        _y=y,
        _frame=1,
        _track_id=track_id,
    )
    detection_2 = create_detection(
        _x=10.0,
        _y=y,
        _frame=2,
        _track_id=track_id,
    )
    detection_3 = create_detection(
        _x=15.0,
        _y=y,
        _frame=3,
        _track_id=track_id,
    )
    detection_4 = create_detection(
        _x=20.0,
        _y=y,
        _frame=4,
        _track_id=track_id,
    )
    detection_5 = create_detection(
        _x=25.0,
        _y=y,
        _frame=5,
        _track_id=track_id,
    )
    return PythonTrack(
        track_id,
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
    def test_detect(self, track: Track) -> None:
        expected_events = create_expected_events(track)
        first_segments = Mock(spec=TrackSegmentDataset)
        first_segments.apply.side_effect = lambda consumer: consumer(
            first_segment_of(track)
        )
        last_segments = Mock(spec=TrackSegmentDataset)
        last_segments.apply.side_effect = lambda consumer: consumer(
            last_segment_of(track)
        )
        mock_tracks = Mock(spec=TrackDataset)
        mock_tracks.get_first_segments.return_value = first_segments
        mock_tracks.get_last_segments.return_value = last_segments

        scene_action_detector = SceneActionDetector()
        events = scene_action_detector.detect(mock_tracks)

        assert events == expected_events

        mock_tracks.get_first_segments.assert_called_once()
        mock_tracks.get_last_segments.assert_called_once()
        first_segments.apply.assert_called_once()
        last_segments.apply.assert_called_once()


def create_expected_events(track: Track) -> list[Event]:
    return create_expected_enter_scene_events(
        track
    ) + create_expected_leave_scene_events(track)


def create_expected_leave_scene_events(track: Track) -> list[Event]:
    occurrence = track.last_detection.occurrence
    event_coordinate = ImageCoordinate(track.last_detection.x, track.last_detection.y)
    return [
        Event(
            road_user_id=track.id.id,
            road_user_type=track.classification,
            hostname=HOSTNAME,
            occurrence=occurrence,
            frame_number=track.last_detection.frame,
            section_id=None,
            event_coordinate=event_coordinate,
            event_type=EventType.LEAVE_SCENE,
            direction_vector=calculate_direction_vector(
                track.detections[-2].x,
                track.detections[-2].y,
                track.last_detection.x,
                track.last_detection.y,
            ),
            video_name=track.first_detection.video_name,
            interpolated_occurrence=occurrence,
            interpolated_event_coordinate=event_coordinate,
        ),
    ]


def create_expected_enter_scene_events(track: Track) -> list[Event]:
    event_coordinate = ImageCoordinate(track.first_detection.x, track.first_detection.y)
    occurrence = track.first_detection.occurrence

    return [
        Event(
            road_user_id=track.id.id,
            road_user_type=track.classification,
            hostname=HOSTNAME,
            occurrence=occurrence,
            frame_number=track.first_detection.frame,
            section_id=None,
            event_coordinate=event_coordinate,
            event_type=EventType.ENTER_SCENE,
            direction_vector=calculate_direction_vector(
                track.first_detection.x,
                track.first_detection.y,
                track.detections[1].x,
                track.detections[1].y,
            ),
            video_name=track.first_detection.video_name,
            interpolated_occurrence=occurrence,
            interpolated_event_coordinate=event_coordinate,
        )
    ]


def first_segment_of(track: Track) -> dict:
    start = track.first_detection
    end = track.detections[1]
    return {
        TRACK_ID: track.id.id,
        TRACK_CLASSIFICATION: track.classification,
        START_X: start.x,
        START_Y: start.y,
        START_OCCURRENCE: start.occurrence,
        START_FRAME: start.frame,
        START_VIDEO_NAME: start.video_name,
        END_X: end.x,
        END_Y: end.y,
        END_OCCURRENCE: end.occurrence,
        END_FRAME: end.frame,
        END_VIDEO_NAME: end.video_name,
    }


def last_segment_of(track: Track) -> dict:
    start = track.detections[-2]
    end = track.last_detection
    return {
        TRACK_ID: track.id.id,
        TRACK_CLASSIFICATION: track.classification,
        START_X: start.x,
        START_Y: start.y,
        START_OCCURRENCE: start.occurrence,
        START_FRAME: start.frame,
        START_VIDEO_NAME: start.video_name,
        END_X: end.x,
        END_Y: end.y,
        END_OCCURRENCE: end.occurrence,
        END_FRAME: end.frame,
        END_VIDEO_NAME: end.video_name,
    }


class TestSceneEventListBuilder:
    def test_create_enter_scene_events(self, track: Track) -> None:
        expected_events = create_expected_enter_scene_events(track)
        segments = Mock(spec=TrackSegmentDataset)
        segments.apply.side_effect = lambda consumer: consumer(first_segment_of(track))

        builder = SceneEventListBuilder()
        builder.add_enter_scene_events(segments)
        events = builder.build()

        assert events == expected_events

        segments.apply.assert_called_once()

    def test_create_leave_scene_events(self, track: Track) -> None:
        expected_events = create_expected_leave_scene_events(track)
        segments = Mock(spec=TrackSegmentDataset)
        segments.apply.side_effect = lambda consumer: consumer(last_segment_of(track))

        builder = SceneEventListBuilder()
        builder.add_leave_scene_events(segments)
        events = builder.build()

        assert events == expected_events

        segments.apply.assert_called_once()
