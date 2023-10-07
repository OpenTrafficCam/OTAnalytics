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
from OTAnalytics.domain.section import LineSection, Section, SectionId
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
        self.track_geom_map: dict[TrackId, Any]
        self.section_geom_map: dict[SectionId, Any]
        self.use_tracks(datastore)
        self.use_sections(datastore)

    @abstractmethod
    def use_tracks(self, datastore: Datastore) -> None:
        pass

    @abstractmethod
    def use_sections(self, datastore: Datastore) -> None:
        pass

    @abstractmethod
    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        pass

    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
        res: set[TrackId] = set()
        for section in sections:
            res = res.union(self.intersects_section(tracks, section))
        return res

    @abstractmethod
    def section_events(self, tracks: list[Track], section: Section) -> EVENTS:
        pass

    @abstractmethod
    def track_events(self, track: Track, sections: list[Section]) -> EVENTS:
        pass

    def events(
        self, tracks: list[Track], sections: list[Section], by_track: bool = False
    ) -> EVENTS:
        if by_track:
            return [e for t in tracks for e in self.track_events(t, sections)]
        else:
            return [e for s in sections for e in self.section_events(tracks, s)]


class OTAIntersect(IntersectProvider):
    def use_tracks(self, datastore: Datastore) -> None:
        self.intersector = SimpleTracksIntersectingSections(
            GetAllTracks(datastore._track_repository), ShapelyIntersector()
        )

    def use_sections(self, datastore: Datastore) -> None:
        pass

    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
        return self.intersector._intersect(tracks, sections)

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        return set()

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

    def events(
        self, tracks: list[Track], sections: list[Section], by_track: bool = False
    ) -> EVENTS:
        return super().events(tracks, sections, by_track=True)


class ShapelyIntersectSingle(IntersectProvider):
    def __init__(self, datastore: Datastore) -> None:
        super().__init__(datastore)

    def use_tracks(self, datastore: Datastore) -> None:
        tracks = datastore.get_all_tracks()
        self.track_geom_map = {track.id: track_to_shapely(track) for track in tracks}
        self.track_projections = {
            track.id: [
                self.track_geom_map[track.id].project(shapely.Point(p))
                for p in self.track_geom_map[track.id].coords
            ]
            for track in tracks
        }

    def use_sections(self, datastore: Datastore) -> None:
        sections = datastore.get_all_sections()
        self.section_geom_map = {
            section.id: section_to_shapely(section) for section in sections
        }

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        sec_geom = self.section_geom_map[section.id]
        return {
            track.id
            for track in tracks
            if shapely_intersects(self.track_geom_map[track.id], sec_geom)
        }

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

    def track_events(self, track: Track, sections: list[Section]) -> EVENTS:
        return [e for s in sections for e in self.single_events(track, s)]

    def section_events(self, tracks: list[Track], section: Section) -> EVENTS:
        return [e for t in tracks for e in self.single_events(t, section)]


class ShapelyIntersect(ShapelyIntersectSingle):
    def __init__(self, datastore: Datastore) -> None:
        super().__init__(datastore)

    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
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
        return set()


# todo shapely segment single
# todo shapley segment


class PyGeosIntersectSingle(IntersectProvider):
    def __init__(self, datastore: Datastore, prepare: bool) -> None:
        self._prepare = prepare
        super().__init__(datastore)

    def use_tracks(self, datastore: Datastore) -> None:
        tracks = datastore.get_all_tracks()

        self.track_geom_map = {track.id: track_to_pygeos(track) for track in tracks}
        self.track_projections = {
            track.id: [
                pygeos_project(self.track_geom_map[track.id], pygeos_points(p))
                for p in pygeos_coords(self.track_geom_map[track.id])
            ]
            for track in tracks
        }

        self.prepare_tracks()

    def use_sections(self, datastore: Datastore) -> None:
        sections = datastore.get_all_sections()

        self.section_geom_map = {
            section.id: section_to_pygeos(section) for section in sections
        }

        self.prepare_sections()

    def prepare_tracks(self) -> None:
        if self._prepare:
            (prepare(geom) for geom in self.track_geom_map.values())

    def prepare_sections(self) -> None:
        if self._prepare:
            (prepare(geom) for geom in self.section_geom_map.values())

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


class PyGeosIntersect(PyGeosIntersectSingle):
    def __init__(self, datastore: Datastore, prepare: bool) -> None:
        super().__init__(datastore, prepare)

    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
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
        return super().intersects_section(tracks, section)


class PyGeosSegmentIntersect(PyGeosIntersect):
    def __init__(self, datastore: Datastore, prepare: bool) -> None:
        super().__init__(datastore, prepare)

    def use_tracks(self, datastore: Datastore) -> None:
        tracks = datastore.get_all_tracks()

        self.track_geom_map = {
            track.id: track_segments_to_pygeos(track) for track in tracks
        }

        self.prepare_tracks()


class PyGeosSegmentIntersectSingle(PyGeosIntersectSingle):
    def __init__(self, datastore: Datastore, prepare: bool) -> None:
        super().__init__(datastore, prepare)

    def use_tracks(self, datastore: Datastore) -> None:
        tracks = datastore.get_all_tracks()

        self.track_geom_map = {
            track.id: track_segments_to_pygeos(track) for track in tracks
        }

        self.prepare_tracks()


class PyGeosPandasIntersectSingle(PyGeosIntersectSingle):
    def __init__(self, datastore: Datastore, prepare: bool) -> None:
        self.track_geom_df = DataFrame(columns=["id", "track", "geom"])
        super().__init__(datastore, prepare)

    def use_tracks(self, datastore: Datastore) -> None:
        tracks = datastore.get_all_tracks()

        self.track_geom_df["track"] = Series(tracks)
        self.track_geom_df["id"] = self.track_geom_df["track"].apply(lambda t: t.id)
        self.track_geom_df["geom"] = self.track_geom_df["track"].apply(
            lambda t: track_to_pygeos(t)
        )

        self.prepare_tracks()

    def prepare_tracks(self) -> None:
        if self._prepare:
            self.track_geom_df["geom"].apply(prepare)

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


class PyGeosPandasIntersect(PyGeosPandasIntersectSingle):
    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
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


class PyGeosPandasCollectionIntersect(PyGeosPandasIntersect):
    def __init__(self, datastore: Datastore, prepare: bool) -> None:
        super().__init__(datastore, prepare)

    def use_tracks(self, datastore: Datastore) -> None:
        tracks = datastore.get_all_tracks()

        self.track_geom_df["track"] = Series(tracks)
        self.track_geom_df["id"] = self.track_geom_df["track"].apply(lambda t: t.id)
        self.track_geom_df["geom"] = self.track_geom_df["track"].apply(
            lambda t: track_segments_to_pygeos(t)
        )

        self.prepare_tracks()


# todo single


class PyGeosPandasSegmentsIntersect(PyGeosIntersect):
    def __init__(self, datastore: Datastore, prepare: bool) -> None:
        super().__init__(datastore, prepare)
        self.detection_df: DataFrame

    def use_tracks(self, datastore: Datastore) -> None:
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

        if self._prepare:
            self.detection_df["segment"].apply(prepare)

    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
        res: set[TrackId] = set()
        for section in sections:
            res = res.union(self.intersects_section(tracks, section))
        return res

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        sec_geom = self.section_geom_map[section.id]
        intersect = (
            self.detection_df["segment"]
            .apply(lambda s: pygeos_intersects(s, sec_geom))
            .astype(bool)
        )
        return {TrackId(i) for i in self.detection_df[intersect]["track_id"].unique()}


# todo single

# GEOPANDAS


class GeoPandasIntersectSingle(IntersectProvider):
    def __init__(self, datastore: Datastore) -> None:
        self.track_df = DataFrame(columns=["id", "track"])
        self.geom_df: GeoDataFrame
        super().__init__(datastore)

    def use_tracks(self, datastore: Datastore) -> None:
        tracks = datastore.get_all_tracks()

        self.track_df["track"] = Series(tracks)
        self.track_df["id"] = self.track_df["track"].apply(lambda t: t.id)

        self.geom_df = GeoDataFrame(
            self.track_df,
            geometry=self.track_df["track"].apply(track_to_shapely),
        )

    def use_sections(self, datastore: Datastore) -> None:
        sections = datastore.get_all_sections()

        self.section_geom_map = {
            section.id: section_to_shapely(section) for section in sections
        }

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        track_ids = [track.id for track in tracks]
        df = self.geom_df[self.geom_df["id"].isin(track_ids)]

        sec_geom = self.section_geom_map[section.id]
        df["intersects"] = self.geom_df.geometry.intersects(sec_geom).astype(bool)

        return set(df[df["intersects"]]["id"].unique())


class GeoPandasIntersect(GeoPandasIntersectSingle):
    def __init__(self, datastore: Datastore) -> None:
        super().__init__(datastore)

    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
        track_ids = [track.id for track in tracks]
        df = self.geom_df[self.geom_df["id"].isin(track_ids)]

        sec_geoms = ShapelyMultiLineString(
            [self.section_geom_map[section.id] for section in sections]
        )
        df["intersects"] = self.geom_df.geometry.intersects(sec_geoms).astype(bool)

        return set(df[df["intersects"]]["id"].unique())

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        return set()


class GeoPandasSegmentIntersectSingle(IntersectProvider):
    def __init__(self, datastore: Datastore) -> None:
        self.track_df = DataFrame(columns=["id", "detection"])
        self.geom_df: GeoDataFrame
        super().__init__(datastore)

    def use_tracks(self, datastore: Datastore) -> None:
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

    def use_sections(self, datastore: Datastore) -> None:
        sections = datastore.get_all_sections()

        self.section_geom_map = {
            section.id: section_to_shapely(section) for section in sections
        }

    def intersects_section(self, tracks: list[Track], section: Section) -> set[TrackId]:
        track_ids = [track.id for track in tracks]
        df = self.geom_df[self.geom_df["id"].isin(track_ids)]

        sec_geom = self.section_geom_map[section.id]
        df["intersects"] = self.geom_df.geometry.intersects(sec_geom).astype(bool)

        return set(df[df["intersects"]]["id"].unique())


class GeoPandasSegmentIntersect(GeoPandasSegmentIntersectSingle):
    def __init__(self, datastore: Datastore) -> None:
        super().__init__(datastore)

    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
        track_ids = [track.id for track in tracks]
        df = self.geom_df[self.geom_df["id"].isin(track_ids)]

        result: list[TrackId] = []
        for section in sections:
            sec_geom = self.section_geom_map[section.id]
            df["intersects"] = self.geom_df.geometry.intersects(sec_geom).astype(bool)

            result += list(df[df["intersects"]]["id"].unique())

        return set(result)


# TODO
# @time
# def tracks_to_segment_linestrings_bulk(tracks: list[Track]):
#    return pygeos.linestrings(
#        [
#            [(f.x, f.y), (s.x, s.y)]
#            for track in tracks
#            for f, s in zip(track.detections[:-1], track.detections[1:])
#        ]
#    )


# @time
# def tracks_to_segment_linestrings_bulk(tracks: list[Track]):
#    return pygeos.linestrings(
#        [
#            [(f.x, f.y), (s.x, s.y)]
#            for track in tracks
#            for f, s in zip(track.detections[:-1], track.detections[1:])
#        ]
#    )

# todo intersect segments
#    def intersect_todo(
#        self, tracks: list[Track], sections: list[Section]
#    ) -> set[TrackId]:
#        return set(
#            track.id
#            for track in tracks
#            if any(
#                any(
#                    intersects(segment, self.section_geom_map[section.id])
#                    for segment in self.track_geom_map[track.id]
#                )
#                for section in sections
#            )
#        )
