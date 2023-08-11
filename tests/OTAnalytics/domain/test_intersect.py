from datetime import datetime
from pathlib import Path

import pytest

from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.intersect import Intersector
from OTAnalytics.domain.track import Detection, TrackId


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


class TestIntersector:
    def test_select_coordinate_in_detection(self, detection: Detection) -> None:
        offset = RelativeOffsetCoordinate(0.5, 0.5)
        coordinate = Intersector._select_coordinate_in_detection(detection, offset)
        assert coordinate.x == detection.x + detection.w * 0.5
        assert coordinate.y == detection.y + detection.h * 0.5
