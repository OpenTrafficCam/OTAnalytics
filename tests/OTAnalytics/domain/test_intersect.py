from datetime import datetime
from pathlib import Path

import pytest

from OTAnalytics.domain.event import EventType
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.intersect import Intersector
from OTAnalytics.domain.section import LineSection, SectionId
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
        video_name="myhostname_something.mp4",
    )


class TestIntersector:
    def test_select_coordinate_in_detection(self, detection: Detection) -> None:
        offset = RelativeOffsetCoordinate(0.5, 0.5)
        coordinate = Intersector._select_coordinate_in_detection(detection, offset)
        assert coordinate.x == detection.x + detection.w * 0.5
        assert coordinate.y == detection.y + detection.h * 0.5

    def test_extract_offset_from_section(self) -> None:
        offset = RelativeOffsetCoordinate(0.5, 0.5)
        section = LineSection(
            SectionId("N"),
            "N",
            {EventType.SECTION_ENTER: offset},
            {},
            coordinates=[Coordinate(0, 0), Coordinate(1, 1)],
        )
        result = Intersector._extract_offset_from_section(
            section, EventType.SECTION_ENTER
        )
        assert result == offset
