from abc import ABC, abstractmethod
from typing import Any

from pandas import DataFrame, Series

# import pygeos
from pygeos import Geometry, geometrycollections, intersects, linestrings, prepare

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.plugin_intersect.shapely.intersect import ShapelyIntersector
from OTAnalytics.plugin_intersect.simple_intersect import (
    SimpleTracksIntersectingSections,
)


class IntersectProvider(ABC):
    def __init__(self) -> None:
        self.track_geom_map: dict[TrackId, Any]
        self.section_geom_map: dict[SectionId, Any]

    @abstractmethod
    def use_tracks(self, datastore: Datastore) -> "IntersectProvider":
        pass

    @abstractmethod
    def use_sections(self, datastore: Datastore) -> "IntersectProvider":
        pass

    @abstractmethod
    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
        pass


class OTAIntersect(IntersectProvider):
    def use_tracks(self, datastore: Datastore) -> IntersectProvider:
        self.intersector = SimpleTracksIntersectingSections(
            GetAllTracks(datastore._track_repository), ShapelyIntersector()
        )
        return self

    def use_sections(self, datastore: Datastore) -> IntersectProvider:
        return self

    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
        return self.intersector._intersect(tracks, sections)


class PyGeosIntersect(IntersectProvider):
    def __init__(self, prepare: bool) -> None:
        super().__init__()

    def use_tracks(self, datastore: Datastore) -> "PyGeosIntersect":
        tracks = datastore.get_all_tracks()

        self.track_geom_map = {
            track.id: self.track_to_linestring(track) for track in tracks
        }

        self.prepare_tracks()

        return self

    def use_sections(self, datastore: Datastore) -> "PyGeosIntersect":
        sections = datastore.get_all_sections()

        self.section_geom_map = {
            section.id: self.section_to_linestring(section) for section in sections
        }

        self.prepare_sections()

        return self

    def prepare_tracks(self) -> None:
        if prepare:
            (prepare(geom) for geom in self.track_geom_map.values())

    def prepare_sections(self) -> None:
        if prepare:
            (prepare(geom) for geom in self.section_geom_map.values())

    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
        return set(
            [
                track.id
                for track in tracks
                if any(
                    intersects(
                        self.track_geom_map[track.id],
                        self.section_geom_map[section.id],
                    )
                    for section in sections
                )
            ]
        )

    def track_to_linestring(self, track: Track) -> Geometry:
        return linestrings([[(d.x, d.y) for d in track.detections]])

    def section_to_linestring(self, section: Section) -> Geometry:
        return linestrings([[(c.x, c.y) for c in section.get_coordinates()]])


class PyGeosSegmentIntersect(PyGeosIntersect):
    def __init__(self, prepare: bool) -> None:
        super().__init__(prepare)

    def use_tracks(self, datastore: Datastore) -> PyGeosIntersect:
        tracks = datastore.get_all_tracks()

        self.track_geom_map = {
            track.id: self.track_to_segment_linestrings(track) for track in tracks
        }

        self.prepare_tracks()

        return self

    def track_to_segment_linestrings(self, track: Track) -> Geometry:
        return geometrycollections(
            linestrings(
                [
                    [(f.x, f.y), (s.x, s.y)]
                    for f, s in zip(track.detections[:-1], track.detections[1:])
                ]
            )
        )

    def intersect_todo(
        self, tracks: list[Track], sections: list[Section]
    ) -> set[TrackId]:
        return set(
            track.id
            for track in tracks
            if any(
                any(
                    intersects(segment, self.section_geom_map[section.id])
                    for segment in self.track_geom_map[track.id]
                )
                for section in sections
            )
        )


class PyGeosPandasIntersect(PyGeosIntersect):
    def __init__(self, prepare: bool) -> None:
        super().__init__(prepare)
        self.track_geom_df = DataFrame(columns=["id", "track", "geom"])

    def use_tracks(self, datastore: Datastore) -> PyGeosIntersect:
        tracks = datastore.get_all_tracks()

        self.track_geom_df["track"] = Series(tracks)
        self.track_geom_df["id"] = self.track_geom_df["track"].apply(lambda t: t.id)
        self.track_geom_df["geom"] = self.track_geom_df["track"].apply(
            lambda t: self.track_to_linestring(t)
        )

        self.prepare_tracks()

        return self

    def prepare_tracks(self) -> None:
        self.track_geom_df["geom"].apply(prepare)

    def intersect(self, tracks: list[Track], sections: list[Section]) -> set[TrackId]:
        track_ids = [track.id for track in tracks]
        df = self.track_geom_df[self.track_geom_df["id"].isin(track_ids)]

        result: set[TrackId] = set()
        for section in sections:
            sec_geom = self.section_geom_map[section.id]
            df["intersects"] = (
                df["geom"].apply(lambda line: intersects(line, sec_geom)).astype(bool)
            )

            result = result.union(set(df[df["intersects"]]["id"].unique()))
        return result

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
