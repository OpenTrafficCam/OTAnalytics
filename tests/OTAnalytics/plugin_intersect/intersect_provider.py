from abc import ABC, abstractmethod
from bisect import bisect
from typing import Any

import shapely
from geopandas import GeoDataFrame
from intersect_data import tracks_as_dataframe
from pandas import DataFrame, Series
from pygeos import Geometry, GeometryType, geometrycollections
from pygeos import get_coordinates as pygeos_coords
from pygeos import get_type_id as pygeos_type
from pygeos import intersection as pygeos_intersection
from pygeos import intersects as pygeos_intersects
from pygeos import is_empty
from pygeos import line_locate_point as pygeos_project
from pygeos import linestrings
from pygeos import points as pygeos_points
from pygeos import prepare
from shapely import LineString as ShapelyLineString
from shapely import MultiLineString as ShapelyMultiLineString
from shapely import intersection as shapely_intersection
from shapely import intersects as shapely_intersects

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.section import LineSection, Section
from OTAnalytics.domain.track import Detection, Track, TrackId
from OTAnalytics.plugin_intersect.shapely.intersect import ShapelyIntersector
from OTAnalytics.plugin_intersect.simple_intersect import (
    SimpleTracksIntersectingSections,
    _run_intersect_on_single_track,
)

OFFSET_X = 0.5
OFFSET_Y = 0.5
EVENTS = list[tuple[float, float]]


def detection_to_coords(d: Detection) -> tuple[float, float]:
    return (d.x + OFFSET_X * d.w, d.y + OFFSET_Y * d.h)


def track_to_shapely(track: Track) -> ShapelyLineString:
    return ShapelyLineString([detection_to_coords(d) for d in track.detections])


def segment_to_shapely(
    frm: tuple[float, float], to: tuple[float, float]
) -> ShapelyLineString:
    return ShapelyLineString([frm, to])


def section_to_shapely(section: Section) -> ShapelyLineString:
    return ShapelyLineString([(c.x, c.y) for c in section.get_coordinates()])


def track_segment_list_to_shapely(track: Track) -> list[ShapelyLineString]:
    return [
        ShapelyLineString(
            [
                detection_to_coords(f),
                detection_to_coords(s),
            ]
        )
        for f, s in zip(track.detections[:-1], track.detections[1:])
    ]


def sections_to_shapely_multi(sections: list[Section]) -> ShapelyMultiLineString:
    return ShapelyMultiLineString([section_to_shapely(sec) for sec in sections])


def track_segments_to_pygeos(track: Track) -> Geometry:
    return geometrycollections(
        linestrings(
            [
                [
                    detection_to_coords(f),
                    detection_to_coords(s),
                ]
                for f, s in zip(track.detections[:-1], track.detections[1:])
            ]
        )
    )


def track_segment_list_to_pygeos(track: Track) -> list[Geometry]:
    return linestrings(
        [
            [
                detection_to_coords(f),
                detection_to_coords(s),
            ]
            for f, s in zip(track.detections[:-1], track.detections[1:])
        ]
    )


def coords_to_pygeos(coord_list: list[tuple[float, float]]) -> Geometry:
    return linestrings([coord_list])


def track_to_pygeos(track: Track) -> Geometry:
    return linestrings([[detection_to_coords(d) for d in track.detections]])


def section_to_pygeos(section: Section) -> Geometry:
    return linestrings([[(c.x, c.y) for c in section.get_coordinates()]])


def sections_to_pygeos_multi(sections: list[Section]) -> Geometry:
    return geometrycollections([section_to_pygeos(s) for s in sections])


class IntersectProvider(ABC):
    def __init__(self, datastore: Datastore) -> None:
        pass

    @abstractmethod
    def do_intersect(
        self, tracks: list[Track], sections: list[Section]
    ) -> set[TrackId]:
        pass

    @abstractmethod
    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        pass

    @abstractmethod
    def intersects_track(self, track: Track, sections: list[Section]) -> set[TrackId]:
        pass

    def intersect(
        self, tracks: list[Track], sections: list[Section], mode: int
    ) -> set[TrackId]:
        if mode == 0:
            return self.do_intersect(tracks, sections)

        res: set[TrackId] = set()
        if mode == 1:
            for section in sections:
                res = res.union(self.intersects_section(tracks, section))
        else:
            for track in tracks:
                res = res.union(self.intersects_track(track, sections))
        return res

    @abstractmethod
    def intersect_modes(self) -> list[int]:
        pass

    @abstractmethod
    def do_events(self, tracks: list[Track], sections: list[Section]) -> EVENTS:
        pass

    @abstractmethod
    def section_events(self, tracks: list[Track], section: Section) -> EVENTS:
        pass

    @abstractmethod
    def track_events(self, track: Track, sections: list[Section]) -> EVENTS:
        pass

    def events(self, tracks: list[Track], sections: list[Section], mode: int) -> EVENTS:
        if mode == 0:
            return self.do_events(tracks, sections)

        if mode == 1:
            return [e for s in sections for e in self.section_events(tracks, s)]
        else:
            return [e for t in tracks for e in self.track_events(t, sections)]

    @abstractmethod
    def event_modes(self) -> list[int]:
        pass


class OTAIntersect(IntersectProvider):
    def __init__(self, datastore: Datastore) -> None:
        self.intersector = SimpleTracksIntersectingSections(
            GetAllTracks(datastore._track_repository), ShapelyIntersector()
        )

    def do_intersect(
        self, tracks: list[Track], sections: list[Section]
    ) -> set[TrackId]:
        return self.intersector._intersect(tracks, sections)

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        return self.do_intersect(tracks, [section])

    def intersects_track(self, track: Track, sections: list[Section]) -> set[TrackId]:
        return self.do_intersect([track], sections)

    def intersect_modes(self) -> list[int]:
        return [0, 1, 2]

    def do_events(
        self, tracks: list[Track], sections: list[Section], by_track: bool = False
    ) -> EVENTS:
        return []

    def section_events(self, tracks: list[Track], section: Section) -> EVENTS:
        return []

    def track_events(self, track: Track, sections: list[Section]) -> EVENTS:
        line_sections = [
            LineSection(
                s.id,
                s.name,
                s.relative_offset_coordinates,
                s.plugin_data,
                s.get_coordinates(),
            )
            for s in sections
        ]
        return [
            (e.event_coordinate.x, e.event_coordinate.y)
            for e in _run_intersect_on_single_track(
                track, line_sections, ShapelyIntersector()
            )
        ]

    def event_modes(self) -> list[int]:
        return [2]


# Shapely


class ShapelyIntersect(IntersectProvider):
    def __init__(self, datastore: Datastore) -> None:
        tracks = datastore.get_all_tracks()
        self.track_geom_map = {track.id: track_to_shapely(track) for track in tracks}
        self.track_projections = {
            track.id: [
                self.track_geom_map[track.id].project(shapely.Point(p))
                for p in self.track_geom_map[track.id].coords
            ]
            for track in tracks
        }

        sections = datastore.get_all_sections()
        self.section_geom_map = {
            section.id: section_to_shapely(section) for section in sections
        }

    def do_intersect(
        self, tracks: list[Track], sections: list[Section]
    ) -> set[TrackId]:
        return {
            track.id
            for track in tracks
            if any(
                shapely_intersects(
                    self.track_geom_map[track.id], self.section_geom_map[section.id]
                )
                for section in sections
            )
        }

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        sec_geom = self.section_geom_map[section.id]
        return {
            track.id
            for track in tracks
            if shapely_intersects(self.track_geom_map[track.id], sec_geom)
        }

    def intersects_track(self, track: Track, sections: list[Section]) -> set[TrackId]:
        track_geom = self.track_geom_map[track.id]
        return (
            {track.id}
            if any(
                shapely_intersects(track_geom, self.section_geom_map[section.id])
                for section in sections
            )
            else set()
        )

    def intersect_modes(self) -> list[int]:
        return [0, 1, 2]

    def next_event(
        self, track: Track, track_geom: Any, point: Any
    ) -> tuple[float, float]:
        dist = track_geom.project(point)
        index = bisect(self.track_projections[track.id], dist)
        return track_geom.coords[index]  # + 1]

    def single_events(self, track: Track, section: Section) -> EVENTS:
        track_geom = self.track_geom_map[track.id]
        section_geom = self.section_geom_map[section.id]
        points = shapely_intersection(track_geom, section_geom)

        if points.is_empty:
            return []

        if isinstance(points, shapely.Point):
            return [self.next_event(track, track_geom, points)]

        if isinstance(points, shapely.MultiPoint):
            return [self.next_event(track, track_geom, p) for p in points.geoms]

        return []

    def do_events(self, tracks: list[Track], sections: list[Section]) -> EVENTS:
        return [e for t in tracks for s in sections for e in self.single_events(t, s)]

    def track_events(self, track: Track, sections: list[Section]) -> EVENTS:
        return [e for s in sections for e in self.single_events(track, s)]

    def section_events(self, tracks: list[Track], section: Section) -> EVENTS:
        return [e for t in tracks for e in self.single_events(t, section)]

    def event_modes(self) -> list[int]:
        return [0, 1, 2]


class ShapelySegmentIntersect(IntersectProvider):
    def __init__(self, datastore: Datastore) -> None:
        tracks = datastore.get_all_tracks()
        self.track_geom_map = {
            track.id: track_segment_list_to_shapely(track) for track in tracks
        }

        sections = datastore.get_all_sections()
        self.section_geom_map = {
            section.id: section_to_shapely(section) for section in sections
        }

    def do_intersect(
        self, tracks: list[Track], sections: list[Section]
    ) -> set[TrackId]:
        return {
            track.id
            for track in tracks
            if any(
                any(
                    shapely_intersects(
                        segment,
                        self.section_geom_map[section.id],
                    )
                    for segment in self.track_geom_map[track.id]
                )
                for section in sections
            )
        }

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        sec_geom = self.section_geom_map[section.id]
        return {
            track.id
            for track in tracks
            if any(
                shapely_intersects(
                    segment,
                    sec_geom,
                )
                for segment in self.track_geom_map[track.id]
            )
        }

    def intersects_track(self, track: Track, sections: list[Section]) -> set[TrackId]:
        track_geom = self.track_geom_map[track.id]
        return (
            {track.id}
            if any(
                any(
                    shapely_intersects(
                        segment,
                        self.section_geom_map[section.id],
                    )
                    for segment in track_geom
                )
                for section in sections
            )
            else set()
        )

    def intersect_modes(self) -> list[int]:
        return [0, 1, 2]

    def do_events(self, tracks: list[Track], sections: list[Section]) -> EVENTS:
        return [
            segment.coords[1]
            for track in tracks
            for segment in self.track_geom_map[track.id]
            if any(
                shapely_intersects(segment, self.section_geom_map[section.id])
                for section in sections
            )
        ]

    def section_events(self, tracks: list[Track], section: Section) -> EVENTS:
        sec_geom = self.section_geom_map[section.id]
        return [
            segment.coords[1]
            for track in tracks
            for segment in self.track_geom_map[track.id]
            if shapely_intersects(segment, sec_geom)
        ]

    def track_events(self, track: Track, sections: list[Section]) -> EVENTS:
        track_geom = self.track_geom_map[track.id]
        return [
            segment.coords[1]
            for segment in track_geom
            if any(
                shapely_intersects(segment, self.section_geom_map[section.id])
                for section in sections
            )
        ]

    def event_modes(self) -> list[int]:
        return [0, 1, 2]


# PyGeos


class PyGeosIntersect(IntersectProvider):
    def __init__(self, datastore: Datastore, _prepare: bool) -> None:
        tracks = datastore.get_all_tracks()
        self.track_geom_map = {track.id: track_to_pygeos(track) for track in tracks}
        self.track_projections = {
            track.id: [
                pygeos_project(self.track_geom_map[track.id], pygeos_points(p))
                for p in pygeos_coords(self.track_geom_map[track.id])
            ]
            for track in tracks
        }

        sections = datastore.get_all_sections()
        self.section_geom_map = {
            section.id: section_to_pygeos(section) for section in sections
        }

        if _prepare:
            (prepare(geom) for geom in self.track_geom_map.values())
            (prepare(geom) for geom in self.section_geom_map.values())

    def do_intersect(
        self, tracks: list[Track], sections: list[Section]
    ) -> set[TrackId]:
        return {
            track.id
            for track in tracks
            if any(
                pygeos_intersects(
                    self.track_geom_map[track.id],
                    self.section_geom_map[section.id],
                )
                for section in sections
            )
        }

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        sec_geom = self.section_geom_map[section.id]
        return {
            track.id
            for track in tracks
            if pygeos_intersects(
                self.track_geom_map[track.id],
                sec_geom,
            )
        }

    def intersects_track(self, track: Track, sections: list[Section]) -> set[TrackId]:
        track_geom = self.track_geom_map[track.id]
        return (
            {track.id}
            if any(
                pygeos_intersects(
                    track_geom,
                    self.section_geom_map[section.id],
                )
                for section in sections
            )
            else set()
        )

    def intersect_modes(self) -> list[int]:
        return [0, 1, 2]

    def next_event(
        self, track: Track, track_geom: Any, point: Any
    ) -> tuple[float, float]:
        dist = pygeos_project(track_geom, point)
        index = bisect(self.track_projections[track.id], dist)
        return pygeos_coords(track_geom)[index]  # + 1]

    def single_events(self, track: Track, section: Section) -> EVENTS:
        track_geom = self.track_geom_map[track.id]
        section_geom = self.section_geom_map[section.id]
        points = pygeos_intersection(track_geom, section_geom)

        if is_empty(points):
            return []

        if pygeos_type(points) == GeometryType.POINT:
            return [self.next_event(track, track_geom, points)]

        if pygeos_type(points) == GeometryType.MULTIPOINT:
            return [
                self.next_event(track, track_geom, pygeos_points(p))
                for p in pygeos_coords(points)
            ]

        return []

    def track_events(self, track: Track, sections: list[Section]) -> EVENTS:
        return [e for s in sections for e in self.single_events(track, s)]

    def section_events(self, tracks: list[Track], section: Section) -> EVENTS:
        return [e for t in tracks for e in self.single_events(t, section)]

    def do_events(self, tracks: list[Track], sections: list[Section]) -> EVENTS:
        return [e for t in tracks for s in sections for e in self.single_events(t, s)]

    def event_modes(self) -> list[int]:
        return [0, 1, 2]


class PyGeosSegmentIntersect(IntersectProvider):
    def __init__(self, datastore: Datastore, _prepare: bool) -> None:
        tracks = datastore.get_all_tracks()
        self.track_geom_map = {
            track.id: track_segment_list_to_pygeos(track) for track in tracks
        }

        sections = datastore.get_all_sections()
        self.section_geom_map = {
            section.id: section_to_pygeos(section) for section in sections
        }

        if _prepare:
            (
                prepare(geom)
                for segments in self.track_geom_map.values()
                for geom in segments
            )
            (prepare(geom) for geom in self.section_geom_map.values())

    def do_intersect(
        self, tracks: list[Track], sections: list[Section]
    ) -> set[TrackId]:
        return {
            track.id
            for track in tracks
            if any(
                any(
                    pygeos_intersects(
                        self.track_geom_map[track.id],
                        self.section_geom_map[section.id],
                    )
                )
                for section in sections
            )
        }

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        sec_geom = self.section_geom_map[section.id]
        return {
            track.id
            for track in tracks
            if any(
                pygeos_intersects(
                    self.track_geom_map[track.id],
                    sec_geom,
                )
            )
        }

    def intersects_track(self, track: Track, sections: list[Section]) -> set[TrackId]:
        track_geom = self.track_geom_map[track.id]
        return (
            {track.id}
            if any(
                any(
                    pygeos_intersects(
                        track_geom,
                        self.section_geom_map[section.id],
                    )
                )
                for section in sections
            )
            else set()
        )

    def intersect_modes(self) -> list[int]:
        return [0, 1, 2]

    def do_events(self, tracks: list[Track], sections: list[Section]) -> EVENTS:
        return [
            pygeos_coords(s)[1]
            for track in tracks
            for s in self.track_geom_map[track.id]
            if any(
                pygeos_intersects(s, self.section_geom_map[section.id])
                for section in sections
            )
        ]

    def section_events(self, tracks: list[Track], section: Section) -> EVENTS:
        sec_geom = self.section_geom_map[section.id]
        return [
            pygeos_coords(s)[1]
            for track in tracks
            for s in self.track_geom_map[track.id]
            if pygeos_intersects(s, sec_geom)
        ]

    def track_events(self, track: Track, sections: list[Section]) -> EVENTS:
        track_geom = self.track_geom_map[track.id]
        return [
            pygeos_coords(s)[1]
            for s in track_geom
            if any(
                pygeos_intersects(s, self.section_geom_map[section.id])
                for section in sections
            )
        ]

    def event_modes(self) -> list[int]:
        return [0, 1, 2]


class PyGeosPandasIntersect(IntersectProvider):
    def __init__(self, datastore: Datastore, _prepare: bool) -> None:
        self.track_geom_df = DataFrame(columns=["id", "track", "geom"])
        tracks = datastore.get_all_tracks()

        self.track_geom_df["track"] = Series(tracks)
        self.track_geom_df["id"] = self.track_geom_df["track"].apply(lambda t: t.id)
        self.track_geom_df["geom"] = self.track_geom_df["track"].apply(
            lambda t: track_to_pygeos(t)
        )

        self.track_geom_df["projection"] = self.track_geom_df["geom"].apply(
            lambda track_geom: [
                pygeos_project(track_geom, pygeos_points(p))
                for p in pygeos_coords(track_geom)
            ]
        )

        sections = datastore.get_all_sections()
        self.section_geom_map = {
            section.id: section_to_pygeos(section) for section in sections
        }

        if _prepare:
            self.track_geom_df["geom"].apply(prepare)
            (prepare(geom) for geom in self.section_geom_map.values())

    def do_intersect(
        self, tracks: list[Track], sections: list[Section]
    ) -> set[TrackId]:
        track_ids = [track.id for track in tracks]
        df = self.track_geom_df[self.track_geom_df["id"].isin(track_ids)]

        sec_geoms = sections_to_pygeos_multi(
            sections
        )  # [self.section_geom_map[section.id] for section in sections]
        df["intersects"] = (
            df["geom"]
            .apply(lambda line: pygeos_intersects(line, sec_geoms))
            .map(any)
            .astype(bool)
        )

        return set(df[df["intersects"]]["id"].unique())

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        track_ids = [track.id for track in tracks]
        df = self.track_geom_df[self.track_geom_df["id"].isin(track_ids)]

        sec_geom = self.section_geom_map[section.id]
        df["intersects"] = (
            df["geom"]
            .apply(lambda line: pygeos_intersects(line, sec_geom))
            .astype(bool)
        )

        return set(df[df["intersects"]]["id"].unique())

    def intersects_track(self, track: Track, sections: list[Section]) -> set[TrackId]:
        return set()

    def intersect_modes(self) -> list[int]:
        return [0, 1]

    def next_event(
        self, track: Track, track_geom: Any, point: Any, projection: Any
    ) -> tuple[float, float]:
        dist = pygeos_project(track_geom, point)
        index = bisect(projection, dist)
        return pygeos_coords(track_geom)[index]  # + 1]

    def do_events(
        self, tracks: list[Track], sections: list[Section], by_track: bool = False
    ) -> EVENTS:
        track_ids = [track.id for track in tracks]
        df = self.track_geom_df[self.track_geom_df["id"].isin(track_ids)]
        sec_geoms = sections_to_pygeos_multi(
            sections
        )  # [self.section_geom_map[section.id] for section in sections]
        df["intersections"] = df["geom"].apply(
            lambda line: [
                i for i in pygeos_intersection(line, sec_geoms) if not is_empty(i)
            ]
        )

        vs = (
            df[df["intersections"].apply(lambda i: len(i) > 0)]
            .apply(
                lambda r: [
                    self.next_event(
                        r["track"], r["geom"], pygeos_points(p), r["projection"]
                    )
                    for p in pygeos_coords(r["intersections"])
                ],
                axis=1,
            )
            .values
        )

        return [v for list in vs for v in list]

    def section_events(self, tracks: list[Track], section: Section) -> EVENTS:
        sec_geom = self.section_geom_map[section.id]
        track_ids = [track.id for track in tracks]
        df = self.track_geom_df[self.track_geom_df["id"].isin(track_ids)]

        df["intersections"] = df["geom"].apply(
            lambda line: pygeos_intersection(line, sec_geom)
        )

        vs = (
            df[df["intersections"].apply(lambda i: not is_empty(i))]
            .apply(
                lambda r: [
                    self.next_event(
                        r["track"], r["geom"], r["intersections"], r["projection"]
                    )
                ]
                if pygeos_type(r["intersections"]) == GeometryType.POINT
                else [
                    self.next_event(
                        r["track"], r["geom"], pygeos_points(p), r["projection"]
                    )
                    for p in pygeos_coords(r["intersections"])
                ],
                axis=1,
            )
            .values
        )

        return [v for list in vs for v in list]

    def track_events(self, track: Track, sections: list[Section]) -> EVENTS:
        return []

    def event_modes(self) -> list[int]:
        return [0, 1]


class PyGeosPandasSegmentIntersect(IntersectProvider):
    def __init__(self, datastore: Datastore, _prepare: bool) -> None:
        self.detection_df = tracks_as_dataframe(datastore)

        self.detection_df["coord"] = self.detection_df.apply(
            detection_to_coords, axis=1
        )
        self.detection_df.drop(self.detection_df.tail(1).index, inplace=True)
        self.detection_df["next"] = (
            self.detection_df["coord"].drop([0]).dropna().reset_index(drop=True)
        )
        self.detection_df["next_id"] = (
            self.detection_df["track_id"].drop([0]).dropna().reset_index(drop=True)
        )
        self.detection_df = self.detection_df[
            self.detection_df["track_id"] == self.detection_df["next_id"]
        ]

        self.detection_df["segment"] = self.detection_df.apply(
            lambda r: coords_to_pygeos([r["coord"], r["next"]]), axis=1
        )

        sections = datastore.get_all_sections()
        self.section_geom_map = {
            section.id: section_to_pygeos(section) for section in sections
        }
        if _prepare:
            self.detection_df["segment"].apply(prepare)
            (prepare(geom) for geom in self.section_geom_map.values())

    def do_intersect(
        self, tracks: list[Track], sections: list[Section]
    ) -> set[TrackId]:
        track_ids = [track.id.id for track in tracks]
        df = self.detection_df[self.detection_df["track_id"].isin(track_ids)]
        intersect = (
            df["segment"]
            .apply(
                lambda s: any(
                    pygeos_intersects(s, self.section_geom_map[section.id])
                    for section in sections
                )
            )
            .astype(bool)
        )
        return {TrackId(i) for i in df[intersect]["track_id"].unique()}

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        sec_geom = self.section_geom_map[section.id]
        track_ids = [track.id.id for track in tracks]
        df = self.detection_df[self.detection_df["track_id"].isin(track_ids)]
        intersect = (
            df["segment"].apply(lambda s: pygeos_intersects(s, sec_geom)).astype(bool)
        )
        return {TrackId(i) for i in df[intersect]["track_id"].unique()}

    def intersects_track(self, track: Track, sections: list[Section]) -> set[TrackId]:
        df = self.detection_df[self.detection_df["track_id"] == track.id.id]
        intersect = (
            df["segment"]
            .apply(
                lambda s: any(
                    pygeos_intersects(s, self.section_geom_map[section.id])
                    for section in sections
                )
            )
            .astype(bool)
        )
        return {TrackId(i) for i in df[intersect]["track_id"].unique()}

    def intersect_modes(self) -> list[int]:
        return [0, 1]

    def do_events(
        self, tracks: list[Track], sections: list[Section], by_track: bool = False
    ) -> EVENTS:
        track_ids = [t.id.id for t in tracks]
        df = self.detection_df[self.detection_df["track_id"].isin(track_ids)]

        return df[
            df["segment"]
            .apply(
                lambda s: any(
                    pygeos_intersects(s, self.section_geom_map[sec.id])
                    for sec in sections
                )
            )
            .astype(bool)
        ]["next"].values

    def section_events(self, tracks: list[Track], section: Section) -> EVENTS:
        track_ids = [t.id.id for t in tracks]
        df = self.detection_df[self.detection_df["track_id"].isin(track_ids)]
        sec_geom = self.section_geom_map[section.id]

        return df[
            df["segment"].apply(lambda s: pygeos_intersects(s, sec_geom)).astype(bool)
        ]["next"].values

    def track_events(self, track: Track, sections: list[Section]) -> EVENTS:
        df = self.detection_df[self.detection_df["track_id"] == track.id.id]

        return df[
            df["segment"]
            .apply(
                lambda s: any(
                    pygeos_intersects(s, self.section_geom_map[sec.id])
                    for sec in sections
                )
            )
            .astype(bool)
        ]["next"].values

    def event_modes(self) -> list[int]:
        return [0, 1]


# GEOPANDAS


class GeoPandasIntersect(IntersectProvider):
    def __init__(self, datastore: Datastore) -> None:
        self.track_df = DataFrame(columns=["id", "track"])
        tracks = datastore.get_all_tracks()

        self.track_df["track"] = Series(tracks)
        self.track_df["id"] = self.track_df["track"].apply(lambda t: t.id)

        self.geom_df = GeoDataFrame(
            self.track_df,
            geometry=self.track_df["track"].apply(track_to_shapely),
        )

        self.geom_df["projection"] = self.geom_df.geometry.apply(
            lambda g: [g.project(shapely.Point(p)) for p in g.coords]
        )

        sections = datastore.get_all_sections()
        self.section_geom_map = {
            section.id: section_to_shapely(section) for section in sections
        }

    def do_intersect(
        self, tracks: list[Track], sections: list[Section]
    ) -> set[TrackId]:
        track_ids = [track.id for track in tracks]
        df = self.geom_df[self.geom_df["id"].isin(track_ids)]

        sec_geoms = ShapelyMultiLineString(
            [self.section_geom_map[section.id] for section in sections]
        )
        df["intersects"] = self.geom_df.geometry.intersects(sec_geoms).astype(bool)

        return set(df[df["intersects"]]["id"].unique())

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        track_ids = [track.id for track in tracks]
        df = self.geom_df[self.geom_df["id"].isin(track_ids)]

        sec_geom = self.section_geom_map[section.id]
        df["intersects"] = self.geom_df.geometry.intersects(sec_geom).astype(bool)

        return set(df[df["intersects"]]["id"].unique())

    def intersects_track(self, track: Track, sections: list[Section]) -> set[TrackId]:
        return set()

    def intersect_modes(self) -> list[int]:
        return [0, 1]

    def next_event(self, row: Any, point: Any) -> tuple[float, float]:
        dist = row["geometry"].project(point)
        index = bisect(row["projection"], dist)
        return row["geometry"].coords[index]  # + 1]

    def single_events(self, row: Any) -> EVENTS:
        points = row["intersection"]
        if isinstance(points, shapely.Point):
            return [self.next_event(row, points)]

        if isinstance(points, shapely.MultiPoint):
            return [self.next_event(row, p) for p in points.geoms]

        return []

    def do_events(self, tracks: list[Track], sections: list[Section]) -> EVENTS:
        track_ids = [track.id for track in tracks]
        df = self.geom_df[self.geom_df["id"].isin(track_ids)]

        sec_geoms = sections_to_shapely_multi(
            sections
        )  # [self.section_geom_map[section.id] for section in sections]
        df["intersection"] = self.geom_df.geometry.intersection(sec_geoms)

        df = df[df["intersection"].apply(lambda g: not g.is_empty).astype(bool)]
        if df.empty:
            return []

        lists = df.apply(lambda row: self.single_events(row), axis=1).values

        return [v for res in lists for v in res]

    def section_events(self, tracks: list[Track], section: Section) -> EVENTS:
        track_ids = [track.id for track in tracks]
        df = self.geom_df[self.geom_df["id"].isin(track_ids)]
        sec_geom = self.section_geom_map[section.id]

        df["intersection"] = self.geom_df.geometry.intersection(sec_geom)
        df = df[df["intersection"].apply(lambda g: not g.is_empty).astype(bool)]

        if df.empty:
            return []

        lists = df.apply(lambda row: self.single_events(row), axis=1).values
        return [v for res in lists for v in res]

    def track_events(self, track: Track, sections: list[Section]) -> EVENTS:
        return []

    def event_modes(self) -> list[int]:
        return [0, 1]


class GeoPandasSegmentIntersect(IntersectProvider):
    def __init__(self, datastore: Datastore) -> None:
        self.track_df = DataFrame(columns=["id", "detection"])
        tracks = datastore.get_all_tracks()
        track_detections = [
            (track.id, detection_to_coords(d))
            for track in tracks
            for d in track.detections
        ]
        ids, detections = zip(*track_detections)
        self.track_df["detection"] = Series(detections)
        self.track_df["id"] = Series(ids)

        self.track_df.drop(self.track_df.tail(1).index, inplace=True)
        self.track_df["next"] = (
            self.track_df["detection"].drop([0]).dropna().reset_index(drop=True)
        )
        self.track_df["next_id"] = (
            self.track_df["id"].drop([0]).dropna().reset_index(drop=True)
        )
        self.track_df = self.track_df[self.track_df["id"] == self.track_df["next_id"]]

        self.geom_df = GeoDataFrame(
            self.track_df,
            geometry=self.track_df.apply(
                lambda r: segment_to_shapely(r["detection"], r["next"]), axis=1
            ),
        )

        sections = datastore.get_all_sections()
        self.section_geom_map = {
            section.id: section_to_shapely(section) for section in sections
        }

    def do_intersect(
        self, tracks: list[Track], sections: list[Section]
    ) -> set[TrackId]:
        track_ids = [track.id for track in tracks]
        df = self.geom_df[self.geom_df["id"].isin(track_ids)]

        sec_geoms = sections_to_shapely_multi(sections)
        df["intersects"] = self.geom_df.geometry.intersects(sec_geoms).astype(bool)

        return set(df[df["intersects"]]["id"].unique())

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        track_ids = [track.id for track in tracks]
        df = self.geom_df[self.geom_df["id"].isin(track_ids)]

        sec_geom = self.section_geom_map[section.id]
        df["intersects"] = self.geom_df.geometry.intersects(sec_geom).astype(bool)

        return set(df[df["intersects"]]["id"].unique())

    def intersects_track(self, track: Track, sections: list[Section]) -> set[TrackId]:
        df = self.geom_df[self.geom_df["id"] == track.id]

        sec_geoms = sections_to_shapely_multi(sections)
        df["intersects"] = self.geom_df.geometry.intersects(sec_geoms).astype(bool)

        return set(df[df["intersects"]]["id"].unique())

    def intersect_modes(self) -> list[int]:
        return [0, 1]

    def do_events(self, tracks: list[Track], sections: list[Section]) -> EVENTS:
        track_ids = [track.id for track in tracks]
        df = self.geom_df[self.geom_df["id"].isin(track_ids)]

        sec_geoms = sections_to_shapely_multi(sections)
        df["intersects"] = self.geom_df.geometry.intersects(sec_geoms).astype(bool)

        return df[df["intersects"]]["next"].values

    def section_events(self, tracks: list[Track], section: Section) -> EVENTS:
        track_ids = [track.id for track in tracks]
        df = self.geom_df[self.geom_df["id"].isin(track_ids)]

        sec_geom = self.section_geom_map[section.id]
        df["intersects"] = self.geom_df.geometry.intersects(sec_geom).astype(bool)

        return df[df["intersects"]]["next"].values

    def track_events(self, track: Track, sections: list[Section]) -> EVENTS:
        df = self.geom_df[self.geom_df["id"] == track.id]

        sec_geoms = sections_to_shapely_multi(sections)
        df["intersects"] = self.geom_df.geometry.intersects(sec_geoms).astype(bool)

        return df[df["intersects"]]["next"].values

    def event_modes(self) -> list[int]:
        return [0, 1]
