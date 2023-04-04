from unittest.mock import Mock

import pytest
from shapely import GeometryCollection, LineString

from OTAnalytics.adapter_intersect.intersect import (
    ShapelyIntersectImplementationAdapter,
)
from OTAnalytics.application.eventlist import SectionActionDetector
from OTAnalytics.domain.event import EventType, SectionEventBuilder
from OTAnalytics.domain.geometry import (
    Coordinate,
    Line,
    Polygon,
    RelativeOffsetCoordinate,
)
from OTAnalytics.domain.intersect import (
    IntersectAreaByTrackPoints,
    IntersectBySmallTrackComponents,
    IntersectBySplittingTrackLine,
)
from OTAnalytics.domain.section import Area, LineSection
from OTAnalytics.domain.track import Track
from OTAnalytics.plugin_intersect.intersect import ShapelyIntersector

FRAME_WIDTH = 800
FRAME_HEIGHT = 600


@pytest.fixture(scope="module")
def shapely_intersection_adapter() -> ShapelyIntersectImplementationAdapter:
    shapely_intersector = ShapelyIntersector()
    return ShapelyIntersectImplementationAdapter(shapely_intersector)


@pytest.fixture(scope="module")
def section_event_builder() -> SectionEventBuilder:
    return SectionEventBuilder()


class TestDetectSectionActivity:
    def test_intersect_by_small_track_components(
        self,
        tracks: list[Track],
        shapely_intersection_adapter: ShapelyIntersectImplementationAdapter,
        section_event_builder: SectionEventBuilder,
    ) -> None:
        # Setup
        line_section = LineSection(
            id="NE",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            start=Coordinate(103, 194),
            end=Coordinate(366, 129),
        )

        line_section_intersector = IntersectBySmallTrackComponents(
            implementation=shapely_intersection_adapter, line_section=line_section
        )

        section_action_detector = SectionActionDetector(
            intersector=line_section_intersector,
            section_event_builder=section_event_builder,
        )

        # Actual usage

        enter_events = section_action_detector.detect_enter_actions(
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
            id="NE",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            start=Coordinate(103, 194),
            end=Coordinate(366, 129),
        )

        line_section_intersector = IntersectBySplittingTrackLine(
            implementation=shapely_intersection_adapter, line_section=line_section
        )

        section_action_detector = SectionActionDetector(
            intersector=line_section_intersector,
            section_event_builder=section_event_builder,
        )

        # Actual usage

        enter_events = section_action_detector.detect_enter_actions(
            sections=[line_section], tracks=tracks
        )
        assert len(enter_events) == 7

    def test_intersect_area_by_track_points(
        self,
        tracks: list[Track],
        shapely_intersection_adapter: ShapelyIntersectImplementationAdapter,
        section_event_builder: SectionEventBuilder,
    ) -> None:
        coordinates: list[Coordinate] = [
            Coordinate(112, 187),
            Coordinate(377, 127),
            Coordinate(467, 118),
            Coordinate(121, 222),
            Coordinate(112, 187),
        ]
        area_section = Area(
            id="NE",
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0),
                EventType.SECTION_LEAVE: RelativeOffsetCoordinate(0, 0),
            },
            plugin_data={},
            coordinates=coordinates,
        )

        area_intersector = IntersectAreaByTrackPoints(
            shapely_intersection_adapter, area_section
        )
        section_action_detector = SectionActionDetector(
            intersector=area_intersector, section_event_builder=section_event_builder
        )
        enter_events = section_action_detector.detect_enter_actions(
            sections=[area_section], tracks=tracks
        )
        assert enter_events
        raise NotImplementedError


class TestShapelyIntersectImplementationAdapter:
    @pytest.fixture
    def first_line(self) -> Line:
        return Line(
            coordinates=[
                Coordinate(0, 10),
                Coordinate(10, 10),
            ],
        )

    @pytest.fixture
    def second_line(self) -> Line:
        return Line(
            coordinates=[
                Coordinate(5, 0),
                Coordinate(5, 10),
            ],
        )

    @pytest.fixture
    def polygon(self) -> Polygon:
        polygon_coordinates = [
            Coordinate(0, 0),
            Coordinate(0, 1),
            Coordinate(1, 1),
            Coordinate(1, 0),
            Coordinate(0, 0),
        ]
        return Polygon(polygon_coordinates)

    def test_line_intersects_line(self, first_line: Line, second_line: Line) -> None:
        mock_shapely_intersector = Mock(spec=ShapelyIntersector)
        mock_shapely_intersector.line_intersects_line.return_value = True

        adapter = ShapelyIntersectImplementationAdapter(mock_shapely_intersector)
        result_intersects = adapter.line_intersects_line(first_line, second_line)

        assert len(mock_shapely_intersector.method_calls) == 1
        assert result_intersects

    def test_line_intersects_polygon(self, first_line: Line, polygon: Polygon) -> None:
        mock_shapely_intersector = Mock(spec=ShapelyIntersector)
        mock_shapely_intersector.line_intersects_polygon.return_value = True

        adapter = ShapelyIntersectImplementationAdapter(mock_shapely_intersector)
        result_intersects = adapter.line_intersects_polygon(first_line, polygon)

        assert len(mock_shapely_intersector.method_calls) == 1
        assert result_intersects

    def test_split_line_with_line_intersection_exists(
        self, first_line: Line, second_line: Line
    ) -> None:
        first_line_string = LineString([[0, 0], [0.5, 0]])
        second_line_string = LineString([[0.5, 0], [1, 0]])

        mock_shapely_intersector = Mock(spec=ShapelyIntersector)
        mock_shapely_intersector.split_line_with_line.return_value = GeometryCollection(
            [first_line_string, second_line_string]
        )

        adapter = ShapelyIntersectImplementationAdapter(mock_shapely_intersector)
        result_splitted_line = adapter.split_line_with_line(first_line, second_line)
        expected = [
            Line([Coordinate(0, 0), Coordinate(0.5, 0)]),
            Line([Coordinate(0.5, 0), Coordinate(1, 0)]),
        ]

        assert len(mock_shapely_intersector.method_calls) == 1
        assert result_splitted_line == expected

    def test_split_line_with_line_no_intersection(
        self, first_line: Line, second_line: Line
    ) -> None:
        line_string = LineString([[0, 0], [1, 0]])

        mock_shapely_intersector = Mock(spec=ShapelyIntersector)
        mock_shapely_intersector.split_line_with_line.return_value = GeometryCollection(
            [line_string]
        )

        adapter = ShapelyIntersectImplementationAdapter(mock_shapely_intersector)
        result_splitted_line = adapter.split_line_with_line(first_line, second_line)

        assert len(mock_shapely_intersector.method_calls) == 1
        assert result_splitted_line is None

    def test_distance_between(self) -> None:
        first_coordinate = Coordinate(0, 0)
        second_coordinate = Coordinate(1, 0)

        mock_shapely_intersector = Mock(spec=ShapelyIntersector)
        mock_shapely_intersector.distance_point_point.return_value = 1

        adapter = ShapelyIntersectImplementationAdapter(mock_shapely_intersector)
        result_splitted_line = adapter.distance_between(
            first_coordinate, second_coordinate
        )

        assert len(mock_shapely_intersector.method_calls) == 1
        assert result_splitted_line == 1

    def test_are_coordinates_within_polygon(self, polygon: Polygon) -> None:
        coordinates = [Coordinate(0, 0), Coordinate(0.5, 0.5), Coordinate(2, 2)]

        mock_shapely_intersector = Mock()
        mock_shapely_intersector.are_points_within_polygon.return_value = [
            False,
            True,
            False,
        ]
        mock_shapely_mapper = Mock()
        mock_shapely_mapper.map_to_tuple_coordinates.return_value = [
            (0, 0),
            (0.5, 0.5),
            (2, 2),
        ]
        adapter = ShapelyIntersectImplementationAdapter(
            mock_shapely_intersector, mock_shapely_mapper
        )

        result_mask = adapter.are_coordinates_within_polygon(coordinates, polygon)

        mock_shapely_mapper.map_to_tuple_coordinates.assert_called_once()
        mock_shapely_intersector.are_points_within_polygon.assert_called_once()
        assert result_mask == [False, True, False]
