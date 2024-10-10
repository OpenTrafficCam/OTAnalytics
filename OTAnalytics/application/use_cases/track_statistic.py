from dataclasses import dataclass

from OTAnalytics.application.use_cases.highlight_intersections import (
    TracksAssignedToAllFlows,
    TracksIntersectingAllSections,
)


@dataclass
class TrackStatistics:
    not_intersection_tracks: int


class CalculateTrackStatistics:
    def __init__(
        self,
        intersection_all_sections: TracksIntersectingAllSections,
        assigned_to_all_flows: TracksAssignedToAllFlows,
    ) -> None:
        self._intersection_all_section = intersection_all_sections
        self._assigned_to_all_flows = assigned_to_all_flows

    def get_statistics(self) -> TrackStatistics:
        return TrackStatistics(42)
