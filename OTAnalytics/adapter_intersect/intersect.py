from OTAnalytics.adapter_intersect.mapping import (
    map_to_shapely_line_string,
    map_to_shapely_polygon,
)
from OTAnalytics.domain.geometry import Line, Polygon
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
