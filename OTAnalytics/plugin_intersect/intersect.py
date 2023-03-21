from typing import Optional

from shapely import GeometryCollection, LineString, Point, Polygon
from shapely.ops import snap, split


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
        return self._complex_split(line, splitter)

    def distance_point_point(self, p1: Point, p2: Point) -> float:
        return p1.distance(p2)

    def _complex_split(
        self, geom: LineString, splitter: LineString | Polygon
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

        if isinstance(splitter, Polygon):
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
