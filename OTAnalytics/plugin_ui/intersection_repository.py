from OTAnalytics.application.use_cases.highlight_intersections import (
    IntersectionRepository,
)
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track_dataset.track_dataset import TrackIdSet


class PythonIntersectionRepository(IntersectionRepository):
    def __init__(self) -> None:
        self._intersections: dict[SectionId, TrackIdSet] = {}

    def store(self, intersections: dict[SectionId, TrackIdSet]) -> None:
        for section, tracks in intersections.items():
            if section in self._intersections:
                self._intersections[section] = self._intersections[section].union(
                    tracks
                )
            else:
                self._intersections[section] = tracks

    def get(self, sections: set[SectionId]) -> dict[SectionId, TrackIdSet]:
        return {
            section: self._intersections[section]
            for section in sections
            if section in self._intersections.keys()
        }

    def get_all(self) -> dict[SectionId, TrackIdSet]:
        return self._intersections.copy()

    def clear(self) -> None:
        self._intersections.clear()

    def remove(self, sections: set[SectionId]) -> None:
        for section in sections:
            if section in self._intersections.keys():
                del self._intersections[section]
