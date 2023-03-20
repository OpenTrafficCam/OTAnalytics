from typing import Optional

from shapely import GeometryCollection, LineString, Point, Polygon
from shapely.ops import split


class ShapelyIntersector:
    def line_intersects_line(self, line_1: LineString, line_2: LineString) -> bool:
        return line_1.intersects(line_2)

    def line_intersects_polygon(self, line: LineString, polygon: Polygon) -> bool:
        return line.intersects(polygon)

    def intersection_line_with_line(
        self, line_1: LineString, line_2: LineString
    ) -> Optional[list[Point]]:
        intersection = line_1.intersection(line_2)
        if not intersection.is_empty:
            try:
                intersection_points: list[Point] = []

                for intersection_point in intersection.geoms:
                    intersection_points.append(intersection_point)
                return intersection_points
            except AttributeError:
                return [intersection]
        return None

    def split_line_with_line(
        self, line: LineString, splitter: LineString
    ) -> GeometryCollection:
        return split(line, splitter)

    def distance_point_point(self, p1: Point, p2: Point) -> float:
        return p1.distance(p2)
