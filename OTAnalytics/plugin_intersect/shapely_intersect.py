from typing import Iterable, Optional

from numpy import ndarray
from shapely import GeometryCollection, LineString, Point, Polygon, contains_xy, prepare
from shapely.ops import snap, split

from OTAnalytics.domain.track import TrackId, TrackListObserver, TrackRepository


class ShapelyIntersector:
    """Provides shapely geometry operations."""

    def line_intersects_line(self, line_1: LineString, line_2: LineString) -> bool:
        """Checks if a line intersects with another line.

        Args:
            line_1 (LineString): the first line
            line_2 (LineString): the second line

        Returns:
            bool: `True` if they intersect. Otherwise `False`.
        """
        return line_1.intersects(line_2)

    def line_intersects_polygon(self, line: LineString, polygon: Polygon) -> bool:
        """Checks if a line intersects with a polygon.

        Args:
            line (LineString): the line
            polygon (Polygon): the polygon

        Returns:
            bool:  `True` if they intersect. Otherwise `False`.
        """
        return line.intersects(polygon)

    def intersection_line_with_line(
        self, line_1: LineString, line_2: LineString
    ) -> Optional[list[Point]]:
        """Calculates the intersection points of to lines if they exist.

        Args:
            line_1 (LineString): the first line to intersect with
            line_2 (LineString): the second line to intersect with

        Returns:
            Optional[list[Point]]: the intersection points if they intersect.
                Otherwise `None`.
        """
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
        """Use a LineString to split another LineString.

        If `line` intersects `splitter` then line_1 will be splitted at the
        intersection points.
        I.e. Let line_1 = [p_1, p_2, ..., p_n], n a natural number and p_x
        the intersection point.

        Then `line` will be splitted as follows:
        [[p_1, p_2, ..., p_x], [p_x, p_(x+1), ..., p_n].

        Args:
            line (LineString): the line to be splitted
            splitter (LineString): the line used for splitting

        Returns:
            GeometryCollection: the splitted lines if they `line` and `splitter`
                intersect. Otherwise the collection contains a single element that is
                the original `line`.
        """
        return self._complex_split(line, splitter)

    def distance_point_point(self, p1: Point, p2: Point) -> float:
        """Calculates the distance between two points.

        Args:
            p1 (Point): the first point to calculate the distance for
            p2 (Point): the second point to calculate the distance for

        Returns:
            float: _description_
        """
        return p1.distance(p2)

    def are_points_within_polygon(
        self, points: list[tuple[float, float]], polygon: Polygon
    ) -> list[bool]:
        """Checks if the points are within the polygon.

        A point is within a polygon if it is enclosed by it. Meaning that a point
        sitting on the boundary of a polygon is treated as not being within it.

        Args:
            points (list[tuple[float, float]]): the points
            polygon (Polygon): the polygon

        Returns:
            list[bool]: the boolean mask holding the information whether a point is
                within a the polygon or not
        """
        prepare(polygon)
        mask: ndarray = contains_xy(polygon, points)
        return mask.tolist()

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


class ShapelyGeometryCache(TrackListObserver):
    def __init__(self, track_repository: TrackRepository) -> None:
        super().__init__()
        self._cache: dict[TrackId, LineString] = dict()
        self._track_repository = track_repository

    def add(self, track_id: TrackId) -> None:
        if not (track := self._track_repository.get_for(track_id)):
            return
        geometry = [
            LineString([[first.x, first.y], [second.x, second.y]])
            for first, second in zip(track.detections[0:-1], track.detections[1:])
        ]
        self._cache[track_id] = geometry

    def add_all(self, track_ids: Iterable[TrackId]) -> None:
        for track_id in track_ids:
            self.add(track_id)

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        self.add_all(tracks)
