from typing import Optional

from OTAnalytics.adapter_intersect.mapping import (
    map_to_domain_line,
    map_to_shapely_line_string,
    map_to_shapely_point,
    map_to_shapely_polygon,
)
from OTAnalytics.domain.geometry import Coordinate, Line, Polygon
from OTAnalytics.domain.intersect import IntersectImplementation
from OTAnalytics.plugin_intersect.intersect import ShapelyIntersector


class ShapelyIntersectImplementationAdapter(IntersectImplementation):
    def __init__(self, shapely_intersector: ShapelyIntersector) -> None:
        self.shapely_intersector = shapely_intersector

    def line_intersects_line(self, line_1: Line, line_2: Line) -> bool:
        shapely_line_1 = map_to_shapely_line_string(line_1)
        shapely_line_2 = map_to_shapely_line_string(line_2)
        return self.shapely_intersector.line_intersects_line(
            shapely_line_1, shapely_line_2
        )

    def line_intersects_polygon(self, line: Line, polygon: Polygon) -> bool:
        shapely_line = map_to_shapely_line_string(line)
        shapely_polygon = map_to_shapely_polygon(polygon)
        return self.shapely_intersector.line_intersects_polygon(
            shapely_line, shapely_polygon
        )

    def split_line_with_line(
        self, line: Line, to_intersect: Line
    ) -> Optional[list[Line]]:
        shapely_line_1 = map_to_shapely_line_string(line)
        shapely_line_2 = map_to_shapely_line_string(to_intersect)
        intersection_points = self.shapely_intersector.split_line_with_line(
            shapely_line_1, shapely_line_2
        )
        if len(intersection_points.geoms) == 1:
            return None

        splitted_lines = [
            map_to_domain_line(line_string) for line_string in intersection_points.geoms
        ]
        return splitted_lines

    def distance_coord_coord(self, p1: Coordinate, p2: Coordinate) -> float:
        shapely_point_1 = map_to_shapely_point(p1)
        shapely_point_2 = map_to_shapely_point(p2)
        return self.shapely_intersector.distance_point_point(
            shapely_point_1, shapely_point_2
        )
