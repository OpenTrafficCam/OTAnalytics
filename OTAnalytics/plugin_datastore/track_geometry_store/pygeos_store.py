from bisect import bisect
from collections import defaultdict
from itertools import chain
from typing import Any, Iterable, Literal

from pandas import DataFrame, concat
from pygeos import (
    Geometry,
    contains,
    geometrycollections,
    get_coordinates,
    intersection,
    intersects,
    is_empty,
    line_locate_point,
    linestrings,
    points,
    polygons,
    prepare,
)

from OTAnalytics.domain import track
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate, apply_offset
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset import (
    IntersectionPoint,
    TrackDataset,
    TrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import PandasTrackDataset

TRACK_ID = "track_id"
GEOMETRY = "geom"
PROJECTION = "projection"
INTERSECTIONS = "intersections"
INTERSECTS = "intersects"
COLUMNS = [GEOMETRY, PROJECTION]
BASE_GEOMETRY = RelativeOffsetCoordinate(0, 0)
ORIENTATION_INDEX: Literal["index"] = "index"


def line_sections_to_pygeos_multi(sections: Iterable[Section]) -> Geometry:
    return geometrycollections([line_section_to_pygeos(s) for s in sections])


def line_section_to_pygeos(section: Section) -> Geometry:
    return linestrings([[(c.x, c.y) for c in section.get_coordinates()]])


def area_sections_to_pygeos(sections: Iterable[Section]) -> list[Geometry]:
    return [area_section_to_pygeos(s) for s in sections]


def area_section_to_pygeos(section: Section) -> Geometry:
    geometry = polygons([[(c.x, c.y) for c in section.get_coordinates()]])
    prepare(geometry)
    return geometry


def create_pygeos_track(
    track: Track, offset: RelativeOffsetCoordinate = BASE_GEOMETRY
) -> Geometry:
    """Creates a prepared pygeos LINESTRING for given track.

    Args:
        track (Track): the track.
        offset (RelativeOffsetCoordinate): the offset to be applied to
            geometry.

    Returns:
        Geometry: the prepared pygeos geometry.
    """
    if offset == BASE_GEOMETRY:
        geometry = linestrings(
            [(detection.x, detection.y) for detection in track.detections]
        )
    else:
        geometry = linestrings(
            [
                apply_offset(detection.x, detection.y, detection.w, detection.h, offset)
                for detection in track.detections
            ]
        )
    prepare(geometry)
    return geometry


class InvalidTrackGeometryDataset(Exception):
    pass


class PygeosTrackGeometryDataset(TrackGeometryDataset):
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
            return PygeosTrackGeometryDataset(offset)
        if isinstance(dataset, PandasTrackDataset):
            return PygeosTrackGeometryDataset(
                offset,
                PygeosTrackGeometryDataset.__create_entries_from_dataframe(
                    dataset, offset
                ),
            )
        track_geom_df = DataFrame.from_dict(
            PygeosTrackGeometryDataset._create_entries(dataset, offset),
            columns=COLUMNS,
            orient=ORIENTATION_INDEX,
        )
        return PygeosTrackGeometryDataset(offset, track_geom_df)

    @staticmethod
    def _create_entries(
        tracks: Iterable[Track], offset: RelativeOffsetCoordinate = BASE_GEOMETRY
    ) -> dict:
        """Create track geometry entries from given tracks.

        The resulting dictionary has following the structure:
        {TRACK_ID: {GEOMETRY: Geometry, PROJECTION: list[float]}}

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
            geometry = create_pygeos_track(_track, offset)
            projection = [
                line_locate_point(geometry, points(p))
                for p in get_coordinates(geometry)
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
        track_size_mask = track_dataset._dataset.groupby(level=0).transform("size")
        filtered_tracks = track_dataset._dataset[track_size_mask > 1]

        if offset == BASE_GEOMETRY:
            new_x = filtered_tracks[track.X]
            new_y = filtered_tracks[track.Y]
        else:
            new_x = filtered_tracks[track.X] + offset.x * filtered_tracks[track.W]
            new_y = filtered_tracks[track.Y] + offset.y * filtered_tracks[track.H]
        tracks = concat([new_x, new_y], keys=[track.X, track.Y], axis=1)
        tracks_by_id = tracks.groupby(level=0, group_keys=True)
        geometries = tracks_by_id.agg(list).apply(
            lambda coords: linestrings(tuple(zip(coords[track.X], coords[track.Y]))),
            axis=1,
        )
        projections = calculate_all_projections(tracks)

        result = concat([geometries, projections], keys=COLUMNS, axis=1)
        return result

    def add_all(self, tracks: Iterable[Track]) -> TrackGeometryDataset:
        if self.empty:
            if isinstance(tracks, PandasTrackDataset):
                return PygeosTrackGeometryDataset(
                    self._offset,
                    self.__create_entries_from_dataframe(tracks, self.offset),
                )
            new_entries = self._create_entries(tracks, self._offset)
            return PygeosTrackGeometryDataset(
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

        return PygeosTrackGeometryDataset(self._offset, new_dataset)

    def remove(self, ids: Iterable[TrackId]) -> TrackGeometryDataset:
        updated = self._dataset.drop(
            index=[track_id.id for track_id in ids], errors="ignore"
        )
        return PygeosTrackGeometryDataset(self._offset, updated)

    def get_for(self, track_ids: Iterable[str]) -> "TrackGeometryDataset":
        _ids = self._dataset.index.intersection(track_ids)

        filtered_df = self._dataset.loc[_ids]
        return PygeosTrackGeometryDataset(self.offset, filtered_df)

    def intersecting_tracks(self, sections: list[Section]) -> set[TrackId]:
        intersecting_tracks = set()
        section_geoms = line_sections_to_pygeos_multi(sections)

        self._dataset[INTERSECTS] = (
            self._dataset[GEOMETRY]
            .apply(lambda line: intersects(line, section_geoms))
            .map(any)
            .astype(bool)
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
        section_geoms = line_sections_to_pygeos_multi(sections)

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
                        points(p),
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
        track_geom: Geometry,
        point: Geometry,
        projection: Any,
    ) -> tuple[TrackId, SectionId, IntersectionPoint]:
        dist = line_locate_point(track_geom, point)
        return (
            TrackId(track_id),
            section_id,
            IntersectionPoint(bisect(projection, dist)),
        )

    def contained_by_sections(
        self, sections: list[Section]
    ) -> dict[TrackId, list[tuple[SectionId, list[bool]]]]:
        contains_result: dict[
            TrackId, list[tuple[SectionId, list[bool]]]
        ] = defaultdict(list)
        for _section in sections:
            section_geom = area_section_to_pygeos(_section)

            contains_masks = self._dataset[GEOMETRY].apply(
                lambda line: [
                    contains(section_geom, points(p))[0] for p in get_coordinates(line)
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
        if not isinstance(other, PygeosTrackGeometryDataset):
            return False
        return self.offset == other.offset and self._dataset[COLUMNS].equals(
            other._dataset[COLUMNS]
        )


def calculate_all_projections(tracks: DataFrame) -> DataFrame:
    tracks_by_id = tracks.groupby(level=0, group_keys=True)
    tracks["last_x"] = tracks_by_id[track.X].shift(1)
    tracks["last_y"] = tracks_by_id[track.Y].shift(1)
    tracks["length_x"] = tracks[track.X] - tracks["last_x"]
    tracks["length_y"] = tracks[track.Y] - tracks["last_y"]
    tracks["pow_x"] = tracks["length_x"].pow(2)
    tracks["pow_y"] = tracks["length_y"].pow(2)
    tracks["sum_x_y_pow"] = tracks["pow_x"] + tracks["pow_y"]
    tracks["distance"] = tracks["sum_x_y_pow"].pow(1 / 2)
    tracks["distance"].fillna(0, inplace=True)
    tracks["cum-distance"] = tracks.groupby(level=0, group_keys=True)[
        "distance"
    ].cumsum()
    return tracks.groupby(level=0, group_keys=True)["cum-distance"].agg(list)
