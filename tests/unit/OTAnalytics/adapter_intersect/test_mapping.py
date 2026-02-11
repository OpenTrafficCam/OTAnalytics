import pytest
from shapely import LineString, Point
from shapely import Polygon as ShapelyPolygon

from OTAnalytics.domain.geometry import Coordinate, Line, Polygon
from OTAnalytics.plugin_intersect.shapely.mapping import ShapelyMapper


class TestShapelyMappers:
    @pytest.mark.parametrize(
        "line,expected",
        [
            (Line([Coordinate(0, 0), Coordinate(1, 0)]), LineString([[0, 0], [1, 0]])),
            (
                Line(
                    [
                        Coordinate(0, 0),
                        Coordinate(1, 0),
                        Coordinate(1, 1),
                        Coordinate(0, 1),
                        Coordinate(0, 0),
                    ]
                ),
                LineString([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]),
            ),
        ],
    )
    def test_map_to_shapely_line_string(self, line: Line, expected: LineString) -> None:
        result = ShapelyMapper.map_to_shapely_line_string(line)

        assert result == expected

    def test_map_to_shapely_polygon(self) -> None:
        coordinates = [
            Coordinate(0, 0),
            Coordinate(1, 0),
            Coordinate(2, 0),
            Coordinate(0, 0),
        ]
        polygon = Polygon(coordinates)
        expected = ShapelyPolygon(((0, 0), (1, 0), (2, 0), (0, 0)))

        result = ShapelyMapper.map_to_shapely_polygon(polygon)

        assert result == expected

    def test_map_to_shapely_point(self) -> None:
        coordinate = Coordinate(0, 0)
        expected = Point(0, 0)

        result = ShapelyMapper.map_to_shapely_point(coordinate)

        assert result == expected

    @pytest.mark.parametrize(
        "line,expected",
        [
            (LineString([[0, 0], [1, 0]]), Line([Coordinate(0, 0), Coordinate(1, 0)])),
            (
                LineString([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]),
                Line(
                    [
                        Coordinate(0, 0),
                        Coordinate(1, 0),
                        Coordinate(1, 1),
                        Coordinate(0, 1),
                        Coordinate(0, 0),
                    ]
                ),
            ),
        ],
    )
    def test_map_to_domain_line(self, line: LineString, expected: Line) -> None:
        result = ShapelyMapper.map_to_domain_line(line)

        assert result == expected
