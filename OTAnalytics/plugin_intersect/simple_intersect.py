from collections import defaultdict
from typing import Iterable

from OTAnalytics.application.analysis.intersect import TracksIntersectingSections
from OTAnalytics.application.geometry import (
    SectionGeometryBuilder,
    TrackGeometryBuilder,
)
from OTAnalytics.application.use_cases.track_repository import (
    GetTracksWithoutSingleDetections,
)
from OTAnalytics.domain.event import EventType
from OTAnalytics.domain.intersect import IntersectImplementation
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import Track, TrackId


class SimpleTracksIntersectingSections(TracksIntersectingSections):
    def __init__(
        self,
        get_tracks: GetTracksWithoutSingleDetections,
        intersect_implementation: IntersectImplementation,
        track_geometry_builder: TrackGeometryBuilder = TrackGeometryBuilder(),
        section_geometry_builder: SectionGeometryBuilder = SectionGeometryBuilder(),
    ):
        self._get_tracks = get_tracks
        self._intersect_implementation = intersect_implementation
        self._track_geometry_builder = track_geometry_builder
        self._section_geometry_builder = section_geometry_builder

    def __call__(self, sections: Iterable[Section]) -> dict[SectionId, set[TrackId]]:
        tracks = self._get_tracks()
        return self._intersect(tracks, sections)

    def _intersect(
        self, tracks: Iterable[Track], sections: Iterable[Section]
    ) -> dict[SectionId, set[TrackId]]:
        print("Number of intersecting tracks per section")
        all_track_ids: dict[SectionId, set[TrackId]] = defaultdict(set)
        for section in sections:
            track_ids = {
                track.id
                for track in tracks
                if self._track_intersects_section(track, section)
            }
            print(f"{section.name}: {len(track_ids)} tracks")
            all_track_ids[section.id].update(track_ids)

        print(f"All sections: {len(all_track_ids)} tracks")
        return all_track_ids

    def _track_intersects_section(self, track: Track, section: Section) -> bool:
        section_offset = section.get_offset(EventType.SECTION_ENTER)
        track_as_geom = self._track_geometry_builder.build(track, section_offset)
        section_as_geom = self._section_geometry_builder.build_as_line(section)
        return self._intersect_implementation.line_intersects_line(
            track_as_geom, section_as_geom
        )
