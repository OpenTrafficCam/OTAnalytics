from functools import lru_cache

from numpy import ndarray
from shapely import GeometryCollection, LineString
from shapely import Polygon as ShapelyPolygon
from shapely import contains_xy, prepare
from shapely.ops import snap, split

from OTAnalytics.domain.geometry import Coordinate, Line, Polygon
from OTAnalytics.domain.intersect import IntersectImplementation
from OTAnalytics.plugin_intersect.shapely.mapping import ShapelyMapper


@lru_cache(maxsize=100000)
def cached_intersects(line_1: LineString, line_2: LineString) -> bool:
    return line_1.intersects(line_2)


class ShapelyIntersector(IntersectImplementation):
    """Provides shapely geometry operations."""

    def __init__(self, mapper: ShapelyMapper = ShapelyMapper()) -> None:
        self._mapper = mapper

    def line_intersects_line(self, line_1: Line, line_2: Line) -> bool:
        """Checks if a line intersects with another line.

        Args:
            line_1 (Line): the first line.
            line_2 (Line): the second line.

        Returns:
            bool: `True` if they intersect. Otherwise `False`.
        """
        shapely_line_1 = self._mapper.map_to_shapely_line_string(line_1)
        shapely_line_2 = self._mapper.map_to_shapely_line_string(line_2)

        return cached_intersects(shapely_line_1, shapely_line_2)

    def line_intersects_polygon(self, line: Line, polygon: Polygon) -> bool:
        """Checks if a line intersects with a polygon.

        Args:
            line (Line): the line.
            polygon (Polygon): the polygon.

        Returns:
            bool:  `True` if they intersect. Otherwise `False`.
        """
        shapely_line = self._mapper.map_to_shapely_line_string(line)
        shapely_polygon = self._mapper.map_to_shapely_polygon(polygon)
        return shapely_line.intersects(shapely_polygon)

    def intersection_line_with_line(
        self, line_1: Line, line_2: Line
    ) -> list[Coordinate]:
        """Calculates the intersection points of to lines if they exist.

        Args:
            line_1 (Line): the first line to intersect with.
            line_2 (Line): the second line to intersect with.

        Returns:
            list[Coordinate]: the intersection points if they intersect.
                Otherwise, `None`.
        """
        shapely_line_1 = self._mapper.map_to_shapely_line_string(line_1)
        shapely_line_2 = self._mapper.map_to_shapely_line_string(line_2)
        intersection = shapely_line_1.intersection(shapely_line_2)
        if intersection.is_empty:
            return []
        else:
            try:
                intersection_points: list[Coordinate] = []

                for intersection_point in intersection.geoms:
                    intersection_points.append(
                        self._mapper.map_to_domain_coordinate(intersection_point)
                    )
                return intersection_points
            except AttributeError:
                return [self._mapper.map_to_domain_coordinate(intersection)]

    def split_line_with_line(self, line: Line, splitter: Line) -> list[Line]:
        """Use a LineString to split another LineString.

        If `line` intersects `splitter` then line_1 will be splitted at the
        intersection points.
        I.e. Let line_1 = [p_1, p_2, ..., p_n], n a natural number and p_x
        the intersection point.

        Then `line` will be splitted as follows:
        [[p_1, p_2, ..., p_x], [p_x, p_(x+1), ..., p_n].

        Args:
            line (Line): the line to be splitted.
            splitter (Line): the line used for splitting.

        Returns:
            list[Line]: the splitted lines.
        """
        shapely_line = self._mapper.map_to_shapely_line_string(line)
        shapely_splitter = self._mapper.map_to_shapely_line_string(splitter)
        intersection_points = self._complex_split(shapely_line, shapely_splitter)
        if len(intersection_points.geoms) == 1:
            # If there are no splits, intersection_points holds a single element
            # that is the original `line`.
            return []

        return [
            self._mapper.map_to_domain_line(line_string)
            for line_string in intersection_points.geoms
        ]

    def distance_between(self, point_1: Coordinate, point_2: Coordinate) -> float:
        """Calculates the distance between two points.

        Args:
            point_1 (Coordinate): the first coordinate to calculate the distance for.
            point_2 (Coordinate): the second coordinate to calculate the distance for.

        Returns:
            float: the unitless distance between p1 and p2.
        """
        shapely_p1 = self._mapper.map_to_shapely_point(point_1)
        shapely_p2 = self._mapper.map_to_shapely_point(point_2)

        return shapely_p1.distance(shapely_p2)

    def are_coordinates_within_polygon(
        self, coordinates: list[Coordinate], polygon: Polygon
    ) -> list[bool]:
        """Checks if the points are within the polygon.

        A point is within a polygon if it is enclosed by it. Meaning that a point
        sitting on the boundary of a polygon is treated as not being within it.

        Args:
            coordinates (list[Coordinate]): the coordinates.
            polygon (Polygon): the polygon.

        Returns:
            list[bool]: the boolean mask holding the information whether a coordinate is
                within the polygon or not.
        """
        shapely_points = self._mapper.map_to_tuple_coordinates(coordinates)
        shapely_polygon = self._mapper.map_to_shapely_polygon(polygon)
        prepare(shapely_polygon)
        mask: ndarray = contains_xy(shapely_polygon, shapely_points)
        return mask.tolist()

    def _complex_split(
        self, geom: LineString, splitter: LineString | ShapelyPolygon
    ) -> GeometryCollection:
        """Split a complex linestring by another geometry without splitting at
        self-intersection points.

        Split a complex linestring using shapely.

        Inspired by https://github.com/Toblerity/Shapely/issues/1068

        Parameters
        ----------
        geom : LineString
            An optionally complex LineString.
        splitter : Geometry
            A geometry to split by.

        Warnings
        --------
        A known vulnerability is where the splitter intersects the complex
        linestring at one of the self-intersecting points of the linestring.
        In this case, only the first path through the self-intersection
        will be split.

        Examples
        --------
        >>> complex_line_string = LineString([(0, 0), (1, 1), (1, 0), (0, 1)])
        >>> splitter = LineString([(0, 0.5), (0.5, 1)])
        >>> complex_split(complex_line_string, splitter).wkt
        'GEOMETRYCOLLECTION (
            LINESTRING (0 0, 1 1, 1 0, 0.25 0.75), LINESTRING (0.25 0.75, 0 1)
        )'

        Return
        ------
        GeometryCollection
            A collection of the geometries resulting from the split.
        """
        if geom.is_simple:
            return split(geom, splitter)

        if isinstance(splitter, ShapelyPolygon):
            splitter = splitter.exterior

        # Ensure that intersection exists and is zero dimensional.
        relate_str = geom.relate(splitter)
        if relate_str[0] == "1":
            raise ValueError(
                "Cannot split LineString by a geometry which intersects a "
                "continuous portion of the LineString."
            )
        if not (relate_str[0] == "0" or relate_str[1] == "0"):
            return GeometryCollection((geom,))

        intersection_points = geom.intersection(splitter)
        # This only inserts the point at the first pass of a self-intersection if
        # the point falls on a self-intersection.
        snapped_geom = snap(
            geom, intersection_points, tolerance=1.0e-12
        )  # may want to make tolerance a parameter.
        # A solution to the warning in the docstring is to roll your own split method
        # here. The current one in shapely returns early when a point is found to be
        # part of a segment. But if the point was at a self-intersection it could be
        # part of multiple segments.
        return split(snapped_geom, intersection_points)
