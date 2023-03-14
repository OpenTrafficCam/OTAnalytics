from shapely import LineString as ShapelyLineString
from shapely import Polygon as ShapelyPolygon

from OTAnalytics.domain.geometry import Line, Polygon


def map_to_shapely_line_string(line: Line) -> ShapelyLineString:
    return ShapelyLineString([[line.start.x, line.start.y], [line.end.x, line.end.y]])


def map_to_shapely_polygon(polygon: Polygon) -> ShapelyPolygon:
    points: list[tuple[float, float]] = [
        (coord.x, coord.y) for coord in polygon.coordinates
    ]
    return ShapelyPolygon(tuple(points))
