from datetime import datetime
from unittest.mock import Mock

import pytest

from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.domain.event import EventType
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import LineSection, SectionId
from OTAnalytics.domain.track import Detection, Track, TrackId
from OTAnalytics.domain.track_dataset import TrackDataset
from OTAnalytics.plugin_datastore.python_track_store import PythonDetection, PythonTrack


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
    _video_name: str = "myhostname_something.mp4",
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
def track_1() -> Track:
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
    def test_detect(
        self,
        track_1: Track,
        track_2: Track,
    ) -> None:
        mock_tracks = Mock(spec=TrackDataset)

        scene_action_detector = SceneActionDetector()
        scene_action_detector.detect(mock_tracks)

        mock_tracks.get_first_segments.assert_called_once()
        mock_tracks.get_last_segments.assert_called_once()
