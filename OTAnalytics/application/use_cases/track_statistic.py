from dataclasses import dataclass

from OTAnalytics.application.use_cases.highlight_intersections import TracksIntersectingAllSections

@dataclass
class TrackStatistics:
    not_intersection_tracks: int

class CalculateTrackStatistics:
    def __init__(self, intersection_all_sections: TracksIntersectingAllSections) -> None:
        self._intersection_all_section = intersection_all_sections
    
    def get_statistics(self) -> TrackStatistics:
        return TrackStatistics(42)
    