from shapely import LineString as ShapelyLineString
from shapely import Point as ShapelyPoint
from shapely import Polygon as ShapelyPolygon

from OTAnalytics.domain.geometry import Coordinate, Line, Polygon


class ShapelyMapper:
    @staticmethod
    def map_to_shapely_line_string(line: Line) -> ShapelyLineString:
        """Map a domain `Line` to a shapely `LineString."""
        points = [[coord.x, coord.y] for coord in line.coordinates]
        return ShapelyLineString(points)

    @staticmethod
    def map_to_shapely_polygon(polygon: Polygon) -> ShapelyPolygon:
        """Map a domain `Polygon` to a shapely `Polygon`."""
        points: list[tuple[float, float]] = [
            (coord.x, coord.y) for coord in polygon.coordinates
        ]
        return ShapelyPolygon(tuple(points))

    @staticmethod
    def map_to_shapely_point(point: Coordinate) -> ShapelyPoint:
        """Map a domain `Coordinate` to a shapely `Point`."""
        return ShapelyPoint(point.x, point.y)

    @staticmethod
    def map_to_domain_line(line: ShapelyLineString) -> Line:
        """Map a shapely `LineString` to a domain `Line` geometry."""
        coords = [Coordinate(coord[0], coord[1]) for coord in line.coords]
        return Line(coords)
