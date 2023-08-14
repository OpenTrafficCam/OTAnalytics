import pytest

from OTAnalytics.domain.geometry import Coordinate, Line, Polygon
from OTAnalytics.plugin_intersect.shapely.intersect import ShapelyIntersector


class TestShapelyIntersector:
    @pytest.fixture
    def polygon(self) -> Polygon:
        return Polygon(
            [
                Coordinate(0, 5),
                Coordinate(5, 1),
                Coordinate(10, 5),
                Coordinate(5, 5),
                Coordinate(0, 5),
            ]
        )

    def test_line_intersects_line_true(self) -> None:
        first_line = Line([Coordinate(0, 0.5), Coordinate(1, 0.5)])
        second_line = Line([Coordinate(0.5, 0), Coordinate(0.5, 1)])

        intersector = ShapelyIntersector()
        intersects = intersector.line_intersects_line(first_line, second_line)

        assert intersects

    def test_line_intersects_line_false(self) -> None:
        first_line = Line([Coordinate(0, 0), Coordinate(10, 0)])
        second_line = Line([Coordinate(0, 5), Coordinate(10, 5)])

        intersector = ShapelyIntersector()
        intersects = intersector.line_intersects_line(first_line, second_line)

        assert not intersects

    def test_line_intersects_polygon_true(self, polygon: Polygon) -> None:
        line = Line([Coordinate(5, 0), Coordinate(5, 10)])

        intersector = ShapelyIntersector()
        intersects = intersector.line_intersects_polygon(line, polygon)

        assert intersects

    def test_line_intersects_polygon_false(self, polygon: Polygon) -> None:
        line = Line([Coordinate(20, 0), Coordinate(20, 10)])

        intersector = ShapelyIntersector()
        intersects = intersector.line_intersects_polygon(line, polygon)

        assert not intersects

    def test_intersection_line_with_line_exists(self) -> None:
        first_line = Line([Coordinate(0, 0.5), Coordinate(1, 0.5)])
        second_line = Line([Coordinate(0.5, 0), Coordinate(0.5, 1)])

        intersector = ShapelyIntersector()
        intersection = intersector.intersection_line_with_line(first_line, second_line)

        assert intersection == [Coordinate(0.5, 0.5)]

    def test_intersection_line_with_line_does_not_exist(self) -> None:
        first_line = Line([Coordinate(0, 0), Coordinate(10, 0)])
        second_line = Line([Coordinate(0, 5), Coordinate(10, 5)])

        intersector = ShapelyIntersector()
        intersection = intersector.intersection_line_with_line(first_line, second_line)

        assert intersection == []

    def test_split_line_with_line_has_intersections(self) -> None:
        first_line = Line([Coordinate(0, 0.5), Coordinate(1, 0.5)])
        splitter = Line([Coordinate(0.5, 0), Coordinate(0.5, 1)])

        intersector = ShapelyIntersector()
        splitted_lines = intersector.split_line_with_line(first_line, splitter)

        expected = [
            Line([Coordinate(0, 0.5), Coordinate(0.5, 0.5)]),
            Line([Coordinate(0.5, 0.5), Coordinate(1, 0.5)]),
        ]
        assert splitted_lines == expected

    def test_split_line_with_line_no_intersections(self) -> None:
        first_line = Line([Coordinate(0, 0), Coordinate(10, 0)])
        splitter = Line([Coordinate(0, 5), Coordinate(10, 5)])

        intersector = ShapelyIntersector()
        splitted_lines = intersector.split_line_with_line(first_line, splitter)

        assert splitted_lines == []

    def test_distance_point_point(self) -> None:
        first_point = Coordinate(0, 0)
        second_point = Coordinate(1, 0)

        intersector = ShapelyIntersector()
        distance = intersector.distance_between(first_point, second_point)

        assert distance == 1

    def test_are_points_within_polygon(self) -> None:
        coords = [
            Coordinate(0.0, 0.0),
            Coordinate(0.0, 1.0),
            Coordinate(1.0, 1.0),
            Coordinate(1.0, 0.0),
            Coordinate(0.0, 0.0),
        ]
        polygon = Polygon(coords)
        points: list[Coordinate] = [
            Coordinate(0.0, 0.0),
            Coordinate(0.5, 0.5),
            Coordinate(2.0, 2.0),
            Coordinate(0.1, 0.0),
        ]

        intersector = ShapelyIntersector()
        result_mask = intersector.are_coordinates_within_polygon(points, polygon)
        expected_mask = [False, True, False, False]

        assert result_mask == expected_mask
