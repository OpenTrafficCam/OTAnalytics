from collections import defaultdict

from OTAnalytics.application.use_cases.highlight_intersections import (
    IntersectionRepository,
)
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import TrackId


class PythonIntersectionRepository(IntersectionRepository):
    def __init__(self) -> None:
        self._intersections: dict[SectionId, set[TrackId]] = defaultdict(set)

    def store(self, intersections: dict[SectionId, set[TrackId]]) -> None:
        for section, tracks in intersections.items():
            self._intersections[section].update(tracks)

    def get(self, sections: set[SectionId]) -> dict[SectionId, set[TrackId]]:
        return {
            key: value for key, value in self._intersections.items() if key in sections
        }