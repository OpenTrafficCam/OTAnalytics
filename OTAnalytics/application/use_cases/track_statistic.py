from dataclasses import dataclass

from OTAnalytics.application.use_cases.highlight_intersections import (
    TracksAssignedToAllFlows,
    TracksIntersectingAllSections,
)


@dataclass
class TrackStatistics:
    number_of_tracks: int
    track_count_outside: int
    track_count_inside: int
    track_count_inside_not_intersecting: int
    track_count_inside_intersecting_but_unassigned: int
    track_count_inside_assigned: int
    percentage_inside_assigned: float


class CalculateTrackStatistics:
    def __init__(
        self,
        intersection_all_sections: TracksIntersectingAllSections,
        assigned_to_all_flows: TracksAssignedToAllFlows,
    ) -> None:
        self._intersection_all_section = intersection_all_sections
        self._assigned_to_all_flows = assigned_to_all_flows

    def get_statistics(self) -> TrackStatistics:
        return TrackStatistics(0, 8, 15, 1, 2, 3, 3.14)
