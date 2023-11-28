from bisect import bisect
from collections import defaultdict
from itertools import chain
from typing import Any, Iterable, Literal, TypedDict

from pandas import DataFrame
from pygeos import (
    Geometry,
    apply,
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

from OTAnalytics.domain.geometry import RelativeOffsetCoordinate, apply_offset
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import (
    IntersectionPoint,
    Track,
    TrackDataset,
    TrackGeometryDataset,
    TrackId,
)

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


class TrackGeometryEntry(TypedDict):
    # TODO: Remove if not needed
    geometry: Geometry
    projection: list[float]


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
        for track in tracks:
            if len(track.detections) < 2:
                # Disregard single detection tracks
                continue
            track_id = track.id.id
            geometry = create_pygeos_track(track, offset)
            projection = [
                line_locate_point(geometry, points(p))
                for p in get_coordinates(geometry)
            ]
            entries[track_id] = {
                GEOMETRY: geometry,
                PROJECTION: projection,
            }
        return entries

    def add_all(self, tracks: Iterable[Track]) -> TrackGeometryDataset:
        if self.empty:
            new_entries = self._create_entries(tracks, self._offset)
            return PygeosTrackGeometryDataset(
                self._offset, DataFrame.from_dict(new_entries, orient=ORIENTATION_INDEX)
            )
        existing_entries = self.as_dict()
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

    def _get_track_geometries_for(self, offset: RelativeOffsetCoordinate) -> DataFrame:
        if (track_df := self._dataset.get(offset, None)) is None:
            self._create_tracks_for(offset)
            track_df = self._dataset[offset]
        return track_df

    def _create_tracks_for(self, offset: RelativeOffsetCoordinate) -> None:
        base_track_geometry = self._dataset[BASE_GEOMETRY]
        self._dataset[offset] = self._apply_offset(base_track_geometry, offset)

    @staticmethod
    def _apply_offset(
        base_track_geometries: DataFrame, offset: RelativeOffsetCoordinate
    ) -> DataFrame:
        new_track_df = base_track_geometries.copy()
        new_track_df[GEOMETRY] = new_track_df[GEOMETRY].apply(
            lambda geom: apply(geom, lambda coord: coord + coord * [offset.x, offset.y])
        )
        new_track_df[PROJECTION] = new_track_df[GEOMETRY].apply(
            lambda track_geom: [
                line_locate_point(track_geom, points(p))
                for p in get_coordinates(track_geom)
            ]
        )
        return new_track_df

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
