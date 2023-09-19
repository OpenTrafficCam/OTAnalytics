from abc import ABC, abstractmethod
from typing import Any

from geopandas import GeoDataFrame
from pandas import DataFrame, Series
from pygeos import Geometry, geometrycollections
from pygeos import intersects as pygeos_intersects
from pygeos import linestrings, prepare
from shapely import LineString as ShapelyLineString
from shapely import intersects as shapely_intersects

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.plugin_intersect.shapely.intersect import ShapelyIntersector
from OTAnalytics.plugin_intersect.simple_intersect import (
    SimpleTracksIntersectingSections,
)

OFFSET_X = 0.5
OFFSET_Y = 0.5


def track_to_shapely(track: Track) -> ShapelyLineString:
    return ShapelyLineString(
        [(d.x + OFFSET_X * d.w, d.y + OFFSET_Y * d.h) for d in track.detections]
    )


def section_to_shapely(section: Section) -> ShapelyLineString:
    return ShapelyLineString([(c.x, c.y) for c in section.get_coordinates()])


def track_segments_to_pygeos(track: Track) -> Geometry:
    return geometrycollections(
        linestrings(
            [
                [
                    (f.x + OFFSET_X * f.w, f.y + OFFSET_Y * f.h),
                    (s.x + OFFSET_X * s.w, s.y + OFFSET_Y * s.h),
                ]
                for f, s in zip(track.detections[:-1], track.detections[1:])
            ]
        )
    )


def track_to_pygeos(track: Track) -> Geometry:
    return linestrings(
        [[(d.x + OFFSET_X * d.w, d.y + OFFSET_Y * d.h) for d in track.detections]]
    )


def section_to_pygeos(section: Section) -> Geometry:
    return linestrings([[(c.x, c.y) for c in section.get_coordinates()]])


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
    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
        pass


# TODO prepare shapely objects
class OTAIntersect(IntersectProvider):
    def use_tracks(self, datastore: Datastore) -> None:
        self.intersector = SimpleTracksIntersectingSections(
            GetAllTracks(datastore._track_repository), ShapelyIntersector()
        )

    def use_sections(self, datastore: Datastore) -> None:
        pass

    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
        return self.intersector._intersect(tracks, sections)


class ShapelyIntersect(IntersectProvider):
    def __init__(self, datastore: Datastore) -> None:
        super().__init__(datastore)

    def use_tracks(self, datastore: Datastore) -> None:
        tracks = datastore.get_all_tracks()
        self.track_geom_map = {track.id: track_to_shapely(track) for track in tracks}

    def use_sections(self, datastore: Datastore) -> None:
        sections = datastore.get_all_sections()
        self.section_geom_map = {
            section.id: section_to_shapely(section) for section in sections
        }

    def intersect(
        self, tracks: list[Track], sections: list[Section]
    ) -> set[TrackId]:  # todo extract method for single section
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


class PyGeosIntersect(IntersectProvider):
    def __init__(self, datastore: Datastore, prepare: bool) -> None:
        self._prepare = prepare
        super().__init__(datastore)

    def use_tracks(self, datastore: Datastore) -> None:
        tracks = datastore.get_all_tracks()

        self.track_geom_map = {track.id: track_to_pygeos(track) for track in tracks}

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

    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
        return set(
            [
                track.id
                for track in tracks
                if any(
                    pygeos_intersects(
                        self.track_geom_map[track.id],
                        self.section_geom_map[section.id],
                    )
                    for section in sections
                )
            ]
        )


class PyGeosSegmentIntersect(PyGeosIntersect):
    def __init__(self, datastore: Datastore, prepare: bool) -> None:
        super().__init__(datastore, prepare)

    def use_tracks(self, datastore: Datastore) -> None:
        tracks = datastore.get_all_tracks()

        self.track_geom_map = {
            track.id: track_segments_to_pygeos(track) for track in tracks
        }

        self.prepare_tracks()


class PyGeosPandasIntersect(PyGeosIntersect):
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

    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
        track_ids = [track.id for track in tracks]
        df = self.track_geom_df[self.track_geom_df["id"].isin(track_ids)]

        result: set[TrackId] = set()
        for section in sections:
            sec_geom = self.section_geom_map[section.id]
            df["intersects"] = (
                df["geom"]
                .apply(lambda line: pygeos_intersects(line, sec_geom))
                .astype(bool)
            )

            result = result.union(set(df[df["intersects"]]["id"].unique()))
        return result


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


class GeoPandasIntersect(IntersectProvider):
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
