from pathlib import Path

import pytest
from shapely import LineString

from OTAnalytics.adapter_intersect.intersect import (
    ShapelyIntersectImplementationAdapter,
)
from OTAnalytics.application.eventlist import SectionActionDetector
from OTAnalytics.domain.event import SectionEventBuilder
from OTAnalytics.domain.geometry import Coordinate
from OTAnalytics.domain.intersect import (
    IntersectBySingleTrackLine,
    IntersectBySmallTrackComponents,
)
from OTAnalytics.domain.section import LineSection
from OTAnalytics.domain.track import Track
from OTAnalytics.plugin_intersect.intersect import ShapelyIntersector
from OTAnalytics.plugin_parser.otvision_parser import OttrkParser

FRAME_WIDTH = 800
FRAME_HEIGHT = 600


@pytest.fixture(scope="module")
def tracks(ottrk_path: Path) -> list[Track]:
    ottrk_parser = OttrkParser()
    return ottrk_parser.parse(ottrk_path)


@pytest.fixture(scope="module")
def shapely_intersection_adapter() -> ShapelyIntersectImplementationAdapter:
    shapely_intersector = ShapelyIntersector()
    return ShapelyIntersectImplementationAdapter(shapely_intersector)


@pytest.fixture(scope="module")
def section_event_builder() -> SectionEventBuilder:
    return SectionEventBuilder()


@pytest.fixture(scope="module")
def ottrk_long_video(test_data_dir: Path) -> Path:
    return test_data_dir / "OTCamera10_FR20_2022-11-03_10-00-00.ottrk"


class TestSectionEventCreator:
    def test_intersect_by_small_track_components(
        self,
        tracks: list[Track],
        shapely_intersection_adapter: ShapelyIntersectImplementationAdapter,
        section_event_builder: SectionEventBuilder,
    ) -> None:
        # Setup
        line_section = LineSection(
            id="NE", start=Coordinate(103, 194), end=Coordinate(366, 129)
        )

        line_section_intersector = IntersectBySmallTrackComponents(
            implementation=shapely_intersection_adapter, line_section=line_section
        )

        section_action_detector = SectionActionDetector(
            intersector=line_section_intersector,
            section_event_builder=section_event_builder,
        )

        # Actual usage

        enter_events = section_action_detector.detect_enter_events(
            sections=[line_section], tracks=tracks
        )
        assert len(enter_events) == 7

    def test_intersect_by_single_track_line(
        self,
        tracks: list[Track],
        shapely_intersection_adapter: ShapelyIntersectImplementationAdapter,
        section_event_builder: SectionEventBuilder,
    ) -> None:
        # Setup
        line_section = LineSection(
            id="NE", start=Coordinate(103, 194), end=Coordinate(366, 129)
        )

        line_section_intersector = IntersectBySingleTrackLine(
            implementation=shapely_intersection_adapter, line_section=line_section
        )

        section_action_detector = SectionActionDetector(
            intersector=line_section_intersector,
            section_event_builder=section_event_builder,
        )

        # Actual usage

        enter_events = section_action_detector.detect_enter_events(
            sections=[line_section], tracks=tracks
        )
        assert len(enter_events) == 7

    def test_sth(self) -> None:
        l1 = LineString([[10, 10], [10, 20]])
        l2 = LineString([[5, 15], [20, 15]])
        x = l1.intersection(l2)
        print(x)
        l3 = LineString([[0, 0], [2, 3], [3, 0], [5, 3], [6, 0]])
        l4 = LineString([[1, 1], [10, 1]])
        x2 = l3.intersection(l4)
        print(x2)
