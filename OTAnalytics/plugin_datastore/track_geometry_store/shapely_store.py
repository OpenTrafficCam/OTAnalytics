from bisect import bisect
from collections import defaultdict
from functools import partial
from itertools import chain
from typing import Any, Iterable, Literal, Sequence

from numpy import dtype, ndarray, object_
from pandas import DataFrame, Series, concat
from shapely import (
    contains,
    from_wkt,
    get_coordinates,
    intersection,
    intersects,
    is_empty,
    line_locate_point,
    prepare,
)
from shapely.geometry import GeometryCollection, LineString, Point, Polygon
from shapely.geometry.base import BaseGeometry

from OTAnalytics.domain import track
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate, apply_offset
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset.track_dataset import (
    IntersectionPoint,
    TrackDataset,
    TrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import LEVEL_TRACK_ID, PandasTrackDataset

TRACK_ID = "track_id"
GEOMETRY = "geom"
PROJECTION = "projection"
INTERSECTIONS = "intersections"
INTERSECTS = "intersects"
COLUMNS = [GEOMETRY, PROJECTION]
BASE_GEOMETRY = RelativeOffsetCoordinate(0, 0)
ORIENTATION_INDEX: Literal["index"] = "index"
NDIGITS_DISTANCE = 5


def line_sections_to_shapely_multi(
    sections: Iterable[Section],
) -> ndarray[Any, dtype[object_]]:
    return from_wkt([str(line_section_to_shapely(s)) for s in sections])


def line_section_to_shapely(section: Section) -> BaseGeometry:
    return LineString([(c.x, c.y) for c in section.get_coordinates()])


def area_sections_to_shapely(sections: Iterable[Section]) -> list[BaseGeometry]:
    return [area_section_to_shapely(s) for s in sections]


def area_section_to_shapely(section: Section) -> BaseGeometry:
    geometry = Polygon([(c.x, c.y) for c in section.get_coordinates()])
    prepare(geometry)
    return geometry


def create_shapely_track(
    track: Track, offset: RelativeOffsetCoordinate = BASE_GEOMETRY
) -> GeometryCollection:
    """Creates a prepared shapely LINESTRING for given track.

    Args:
        track (Track): the track.
        offset (RelativeOffsetCoordinate): the offset to be applied to
            geometry.

    Returns:
        GeometryCollection: the prepared shapely geometry.
    """
    if offset == BASE_GEOMETRY:
        geometry = LineString(
            [(detection.x, detection.y) for detection in track.detections]
        )
    else:
        geometry = LineString(
            [
                apply_offset(detection.x, detection.y, detection.w, detection.h, offset)
                for detection in track.detections
            ]
        )
    prepare(geometry)
    return GeometryCollection(geometry)


class InvalidTrackGeometryDataset(Exception):
    pass


def distance_on_track(point: Point, track_geom: GeometryCollection) -> float:
    distance = line_locate_point(track_geom, point)
    return round(distance, NDIGITS_DISTANCE)


class ShapelyTrackGeometryDataset(TrackGeometryDataset):
    def __init__(
        self,
        offset: RelativeOffsetCoordinate,
        dataset: DataFrame | None = None,
    ):
        self._offset = offset
        if dataset is None:
            self._dataset = self._create_empty()
        else:
            self._dataset = dataset

    def _create_empty(self) -> DataFrame:
        return DataFrame(columns=COLUMNS)

    @property
    def track_ids(self) -> set[str]:
        return set(self._dataset.index)

    @property
    def offset(self) -> RelativeOffsetCoordinate:
        return self._offset

    @property
    def empty(self) -> bool:
        """Whether dataset is empty.

        Returns:
            bool: True if dataset is empty, False otherwise.
        """
        return self._dataset.empty

    @staticmethod
    def from_track_dataset(
        dataset: TrackDataset, offset: RelativeOffsetCoordinate
    ) -> TrackGeometryDataset:
        if len(dataset) == 0:
            return ShapelyTrackGeometryDataset(offset)
        if isinstance(dataset, PandasTrackDataset):
            return ShapelyTrackGeometryDataset(
                offset,
                ShapelyTrackGeometryDataset.__create_entries_from_dataframe(
                    dataset, offset
                ),
            )
        track_geom_df = DataFrame.from_dict(
            ShapelyTrackGeometryDataset._create_entries(dataset, offset),
            columns=COLUMNS,
            orient=ORIENTATION_INDEX,
        )
        return ShapelyTrackGeometryDataset(offset, track_geom_df)

    @staticmethod
    def _create_entries(
        tracks: Iterable[Track], offset: RelativeOffsetCoordinate = BASE_GEOMETRY
    ) -> dict:
        """Create track geometry entries from given tracks.

        The resulting dictionary has following the structure:
        {TRACK_ID: {GEOMETRY: BaseGeometry, PROJECTION: list[float]}}

        Args:
            tracks (Iterable[Track]): the tracks to create the entries from.
            offset (RelativeOffsetCoordinate): the offset to apply to the tracks.
                Defaults to BASE_GEOMETRY.

        Returns:
            dict: the entries.
        """
        entries = dict()
        for _track in tracks:
            if len(_track.detections) < 2:
                # Disregard single detection tracks
                continue
            track_id = _track.id.id
            geometry = create_shapely_track(_track, offset)
            projection = [
                distance_on_track(Point(p), geometry) for p in get_coordinates(geometry)
            ]
            entries[track_id] = {
                GEOMETRY: geometry,
                PROJECTION: projection,
            }
        return entries

    @staticmethod
    def __create_entries_from_dataframe(
        track_dataset: PandasTrackDataset,
        offset: RelativeOffsetCoordinate,
    ) -> DataFrame:
        track_size_mask = track_dataset._dataset.groupby(
            level=LEVEL_TRACK_ID
        ).transform("size")
        filtered_tracks = track_dataset._dataset[track_size_mask > 1]

        if offset == BASE_GEOMETRY:
            new_x = filtered_tracks[track.X]
            new_y = filtered_tracks[track.Y]
        else:
            new_x = filtered_tracks[track.X] + offset.x * filtered_tracks[track.W]
            new_y = filtered_tracks[track.Y] + offset.y * filtered_tracks[track.H]
        tracks = concat([new_x, new_y], keys=[track.X, track.Y], axis=1)
        tracks_by_id = tracks.groupby(level=LEVEL_TRACK_ID, group_keys=True)
        geometries = tracks_by_id.apply(convert_to_linestrings)
        projections = calculate_all_projections(tracks)

        result = concat([geometries, projections], keys=COLUMNS, axis=1)
        return result

    def add_all(self, tracks: Iterable[Track]) -> TrackGeometryDataset:
        if self.empty:
            if isinstance(tracks, PandasTrackDataset):
                return ShapelyTrackGeometryDataset(
                    self._offset,
                    self.__create_entries_from_dataframe(tracks, self.offset),
                )
            new_entries = self._create_entries(tracks, self._offset)
            return ShapelyTrackGeometryDataset(
                self._offset, DataFrame.from_dict(new_entries, orient=ORIENTATION_INDEX)
            )
        existing_entries = self.as_dict()
        if isinstance(tracks, PandasTrackDataset):
            new_entries = self.__create_entries_from_dataframe(
                tracks, self._offset
            ).to_dict(orient=ORIENTATION_INDEX)
        else:
            new_entries = self._create_entries(tracks, self._offset)
        for track_id, entry in new_entries.items():
            existing_entries[track_id] = entry
        new_dataset = DataFrame.from_dict(existing_entries, orient=ORIENTATION_INDEX)

        return ShapelyTrackGeometryDataset(self._offset, new_dataset)

    def remove(self, ids: Sequence[str]) -> TrackGeometryDataset:
        updated = self._dataset.drop(index=ids, errors="ignore")
        return ShapelyTrackGeometryDataset(self._offset, updated)

    def get_for(self, track_ids: list[str]) -> "TrackGeometryDataset":
        _ids = self._dataset.index.intersection(track_ids)

        filtered_df = self._dataset.loc[_ids]
        return ShapelyTrackGeometryDataset(self.offset, filtered_df)

    def intersecting_tracks(self, sections: list[Section]) -> set[TrackId]:
        intersecting_tracks = set()
        section_geoms = line_sections_to_shapely_multi(sections)
        prepared_function = partial(calculate_intersects, section_geoms=section_geoms)

        self._dataset[INTERSECTS] = (
            self._dataset[GEOMETRY].apply(prepared_function).map(any).astype(bool)
        )
        track_ids = [
            TrackId(_id) for _id in self._dataset[self._dataset[INTERSECTS]].index
        ]
        intersecting_tracks.update(track_ids)

        return intersecting_tracks

    def intersection_points(
        self, sections: list[Section]
    ) -> dict[TrackId, list[tuple[SectionId, IntersectionPoint]]]:
        intersection_points = defaultdict(list)
        section_geoms = line_sections_to_shapely_multi(sections)

        self._dataset[INTERSECTIONS] = self._dataset[GEOMETRY].apply(
            lambda line: [
                (sections[index].id, ip)
                for index, ip in enumerate(intersection(line, section_geoms))
                if not is_empty(ip)
            ]
        )
        intersections = (
            self._dataset[self._dataset[INTERSECTIONS].apply(lambda i: len(i) > 0)]
            .apply(
                lambda r: [
                    self._next_event(
                        r.name,  # the track id (track ids is used as df index)
                        _section_id,
                        r[GEOMETRY],
                        Point(p),
                        r[PROJECTION],
                    )
                    for _section_id, ip in r[INTERSECTIONS]
                    for p in get_coordinates(ip)
                ],
                axis=1,
            )
            .values
        )
        for _id, section_id, intersection_point in chain.from_iterable(intersections):
            intersection_points[_id].append((section_id, intersection_point))

        return intersection_points

    def _next_event(
        self,
        track_id: str,
        section_id: SectionId,
        track_geom: GeometryCollection,
        point: Point,
        projection: Any,
    ) -> tuple[TrackId, SectionId, IntersectionPoint]:
        dist, upper_index = self.__get_distance_and_index(point, projection, track_geom)
        lower_index = upper_index - 1
        lower_distance = projection[lower_index]
        upper_distance = projection[upper_index]
        relative_position = (dist - lower_distance) / (upper_distance - lower_distance)
        return (
            TrackId(track_id),
            section_id,
            IntersectionPoint(
                upper_index=upper_index,
                relative_position=relative_position,
            ),
        )

    @staticmethod
    def __get_distance_and_index(
        point: Point, projection: Any, track_geom: GeometryCollection
    ) -> tuple[float, int]:
        """
        Computes the distance along the track and identifies the corresponding index of
        the projection list. This utility function determines whether the input point is
        within the projected range on the geometry track and calculates its distance and
        projection index accordingly.

        Args:
            point (Point): The geometry point whose distance along the track is
                to be computed.
            projection (Any): A list of pre-computed projection distances along the
                track.
            track_geom (GeometryCollection): The geometry of the track used for distance
                computation.

        Returns:
            tuple[float, int]: A tuple containing the computed distance along the track
            and its corresponding index in the projection list.
        """
        dist = distance_on_track(point, track_geom)
        if dist < projection[-1]:
            upper_index = bisect(projection, dist)
            return dist, upper_index

        max_index = len(projection) - 1
        bounded_dist = projection[-1]
        return bounded_dist, max_index

    def contained_by_sections(
        self, sections: list[Section]
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        contains_result: dict[TrackId, list[tuple[SectionId, list[bool]]]] = (
            defaultdict(list)
        )
        for _section in sections:
            section_geom = area_section_to_shapely(_section)

            contains_masks = self._dataset[GEOMETRY].apply(
                lambda line: [
                    contains(section_geom, Point(p)) for p in get_coordinates(line)
                ]
            )
            tracks_contained = contains_masks[contains_masks.map(any)]

            if tracks_contained.empty:
                continue

            tracks_contained.index = tracks_contained.index.map(TrackId)
            for track_id, contains_mask in tracks_contained.to_dict().items():
                contains_result[track_id].append((_section.id, contains_mask))
        return contains_result

    def as_dict(self) -> dict:
        return self._dataset[COLUMNS].to_dict(orient=ORIENTATION_INDEX)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ShapelyTrackGeometryDataset):
            return False
        return self.offset == other.offset and self._dataset[COLUMNS].equals(
            other._dataset[COLUMNS]
        )


def calculate_intersects(line: BaseGeometry, section_geoms: Any) -> bool:
    return intersects(line, section_geoms)


def calculate_all_projections(tracks: DataFrame) -> Series:
    tracks_by_id = tracks.groupby(level=0, group_keys=True)
    tracks["last_x"] = tracks_by_id[track.X].shift(1)
    tracks["last_y"] = tracks_by_id[track.Y].shift(1)
    tracks["length_x"] = tracks[track.X] - tracks["last_x"]
    tracks["length_y"] = tracks[track.Y] - tracks["last_y"]
    tracks["pow_x"] = tracks["length_x"].pow(2)
    tracks["pow_y"] = tracks["length_y"].pow(2)
    tracks["sum_x_y_pow"] = tracks["pow_x"] + tracks["pow_y"]
    tracks["distance"] = tracks["sum_x_y_pow"].pow(1 / 2)
    tracks["distance"] = tracks["distance"].fillna(0)
    tracks["cum-distance"] = tracks.groupby(level=0, group_keys=True)[
        "distance"
    ].cumsum()
    return tracks.groupby(level=0, group_keys=True)["cum-distance"].agg(list)


def convert_to_linestrings(coords: DataFrame) -> Any:
    return LineString(list(zip(coords[track.X], coords[track.Y])))
