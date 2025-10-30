from typing import Iterable

from OTAnalytics.application.analysis.intersect import TracksIntersectingSections
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track_dataset.track_dataset import TrackIdSet
from OTAnalytics.domain.types import EventType


class SimpleTracksIntersectingSections(TracksIntersectingSections):
    def __init__(self, get_tracks: GetAllTracks):
        self._get_tracks = get_tracks

    def __call__(self, sections: Iterable[Section]) -> dict[SectionId, TrackIdSet]:
        return self.intersect(sections)

    def intersect(self, sections: Iterable[Section]) -> dict[SectionId, TrackIdSet]:
        track_dataset = self._get_tracks.as_dataset()
        result: dict[SectionId, TrackIdSet] = {}
        total_tracks_intersected = 0
        print("Number of intersecting tracks per section")
        for section in sections:
            intersecting_tracks = track_dataset.intersecting_tracks(
                [section], section.get_offset(EventType.SECTION_ENTER)
            )
            result[section.id] = intersecting_tracks
            num_tracks_intersected = len(intersecting_tracks)
            total_tracks_intersected += num_tracks_intersected
            print(f"{section.name}: {num_tracks_intersected} tracks")
        print(f"All sections: {total_tracks_intersected} tracks")
        return result
