from shapely import LineString, Point
from shapely import Polygon as ShapelyPolygon

from OTAnalytics.adapter_intersect.mapping import (
    map_to_domain_line,
    map_to_shapely_line_string,
    map_to_shapely_point,
    map_to_shapely_polygon,
)
from OTAnalytics.domain.geometry import Coordinate, Line, Polygon


class TestShapelyMappers:
    def test_map_to_shapely_line_string(self) -> None:
        first_coordinate = Coordinate(0, 0)
        second_coordinate = Coordinate(1, 0)
        line = Line([first_coordinate, second_coordinate])
        expected = LineString([[0, 0], [1, 0]])

        result = map_to_shapely_line_string(line)

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

        result = map_to_shapely_polygon(polygon)

        assert result == expected

    def test_map_to_shapely_point(self) -> None:
        coordinate = Coordinate(0, 0)
        expected = Point(0, 0)

        result = map_to_shapely_point(coordinate)

        assert result == expected

    def test_map_to_domain_line(self) -> None:
        line_string = LineString([[0, 0], [1, 0]])
        expected = Line([Coordinate(0, 0), Coordinate(1, 0)])

        result = map_to_domain_line(line_string)

        assert result == expected
