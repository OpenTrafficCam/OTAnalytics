from typing import Optional

from OTAnalytics.adapter_intersect.mapping import ShapelyMapper
from OTAnalytics.domain.geometry import Coordinate, Line, Polygon
from OTAnalytics.domain.intersect import IntersectImplementation
from OTAnalytics.plugin_intersect.intersect import ShapelyIntersector


class ShapelyIntersectImplementationAdapter(IntersectImplementation):
    """Adapts a `ShapelyIntersector` to conform to `IntersectImplentation interface.

    Args:
        shapely_intersector (ShapelyIntersector): the shapely intersector
        shapely_mapper (ShapelyMapper, optional): the mapper to convert domain
            geometries to shapely geometries and vice versa. Defaults to
            ShapelyMapper().
    """

    def __init__(
        self,
        shapely_intersector: ShapelyIntersector,
        shapely_mapper: ShapelyMapper = ShapelyMapper(),
    ) -> None:
        self.shapely_intersector = shapely_intersector
        self.mapper = shapely_mapper

    def line_intersects_line(self, line_1: Line, line_2: Line) -> bool:
        shapely_line_1 = self.mapper.map_to_shapely_line_string(line_1)
        shapely_line_2 = self.mapper.map_to_shapely_line_string(line_2)
        return self.shapely_intersector.line_intersects_line(
            shapely_line_1, shapely_line_2
        )

    def line_intersects_polygon(self, line: Line, polygon: Polygon) -> bool:
        shapely_line = self.mapper.map_to_shapely_line_string(line)
        shapely_polygon = self.mapper.map_to_shapely_polygon(polygon)
        return self.shapely_intersector.line_intersects_polygon(
            shapely_line, shapely_polygon
        )

    def split_line_with_line(
        self, line: Line, to_intersect: Line
    ) -> Optional[list[Line]]:
        shapely_line_1 = self.mapper.map_to_shapely_line_string(line)
        shapely_line_2 = self.mapper.map_to_shapely_line_string(to_intersect)
        intersection_points = self.shapely_intersector.split_line_with_line(
            shapely_line_1, shapely_line_2
        )
        if len(intersection_points.geoms) == 1:
            return None

        return [
            self.mapper.map_to_domain_line(line_string)
            for line_string in intersection_points.geoms
        ]

    def distance_between(self, point_1: Coordinate, point_2: Coordinate) -> float:
        shapely_point_1 = self.mapper.map_to_shapely_point(point_1)
        shapely_point_2 = self.mapper.map_to_shapely_point(point_2)
        return self.shapely_intersector.distance_point_point(
            shapely_point_1, shapely_point_2
        )

    def are_coordinates_within_polygon(
        self, coordinates: list[Coordinate], polygon: Polygon
    ) -> list[bool]:
        points = self.mapper.map_to_tuple_coordinates(coordinates)
        shapely_polygon = self.mapper.map_to_shapely_polygon(polygon)
        return self.shapely_intersector.are_points_within_polygon(
            points, shapely_polygon
        )
