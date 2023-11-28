from collections import defaultdict
from typing import Iterable

from OTAnalytics.application.analysis.intersect import TracksIntersectingSections
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.section import Section, SectionId
from OTAnalytics.domain.track import TrackId
from OTAnalytics.domain.types import EventType


class SimpleTracksIntersectingSections(TracksIntersectingSections):
    def __init__(self, get_tracks: GetAllTracks):
        self._get_tracks = get_tracks

    def __call__(self, sections: Iterable[Section]) -> dict[SectionId, set[TrackId]]:
        return self.intersect(sections)

    def intersect(self, sections: Iterable[Section]) -> dict[SectionId, set[TrackId]]:
        track_dataset = self._get_tracks.as_dataset()
        result = defaultdict(set)
        total_tracks_intersected = 0
        print("Number of intersecting tracks per section")
        for section in sections:
            result[section.id].update(
                track_dataset.intersecting_tracks(
                    [section], section.get_offset(EventType.SECTION_ENTER)
                )
            )
            num_tracks_intersected = len(result[section.id])
            total_tracks_intersected += num_tracks_intersected
            print(f"{section.name}: {num_tracks_intersected} tracks")
        print(f"All sections: {total_tracks_intersected} tracks")
        return result
