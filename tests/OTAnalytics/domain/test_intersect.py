from datetime import datetime

import pytest

from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.intersect import Intersector
from OTAnalytics.domain.track import Detection, PythonDetection, TrackId


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


class TestIntersector:
    def test_select_coordinate_in_detection(self, detection: Detection) -> None:
        offset = RelativeOffsetCoordinate(0.5, 0.5)
        coordinate = Intersector._select_coordinate_in_detection(detection, offset)
        assert coordinate.x == detection.x + detection.w * 0.5
        assert coordinate.y == detection.y + detection.h * 0.5
