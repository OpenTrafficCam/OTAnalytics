from dataclasses import dataclass

from OTAnalytics.application.use_cases.highlight_intersections import (
    TracksAssignedToAllFlows,
    TracksInsideCuttingSections,
    TracksIntersectingAllSections,
    TracksOnlyOutsideCuttingSections,
)
from OTAnalytics.application.use_cases.track_repository import GetAllTrackIds

START_OF_CUTTING_SECTION_NAME: str = "#clicut"


@dataclass
class TrackStatistics:
    track_count: int
    track_count_outside: int
    track_count_inside: int
    track_count_inside_not_intersecting: int
    track_count_inside_intersecting_but_unassigned: int
    track_count_inside_assigned: int
    percentage_inside_assigned: float

    def __str__(self) -> str:
        # TODO round percentage
        return (
            f"{self.track_count_inside} of the "
            f"{self.track_count} tracks are inside the cutting section."
            f"{self.track_count_inside_assigned} "
            f"({int(self.percentage_inside_assigned * 100)}%) "
            f"of these are assigned to flows, "
            f"{self.track_count_inside_not_intersecting} "
            f"do not intersect any section."
        )


class CalculateTrackStatistics:
    def __init__(
        self,
        intersection_all_sections: TracksIntersectingAllSections,
        assigned_to_all_flows: TracksAssignedToAllFlows,
        get_all_track_ids: GetAllTrackIds,
        inside_cutting_sections: TracksInsideCuttingSections,
        outside_cutting_sections: TracksOnlyOutsideCuttingSections,
    ) -> None:
        self._intersection_all_section = intersection_all_sections
        self._assigned_to_all_flows = assigned_to_all_flows
        self._get_all_track_ids = get_all_track_ids
        self._inside_cutting_sections = inside_cutting_sections
        self._outside_cutting_sections = outside_cutting_sections

    def get_statistics(self) -> TrackStatistics:
        track_count_inside = len(self._inside_cutting_sections.get_ids())
        track_count_outside = len(self._outside_cutting_sections.get_ids())
        track_count = len(set(self._get_all_track_ids()))

        track_count_inside_not_intersecting = len(
            self._inside_cutting_sections.get_ids().difference(
                self._intersection_all_section.get_ids()
            )
        )
        track_count_inside_assigned = len(
            self._inside_cutting_sections.get_ids().intersection(
                self._assigned_to_all_flows.get_ids()
            )
        )
        track_count_inside_intersecting_but_unassigned = (
            track_count_inside
            - track_count_inside_not_intersecting
            - track_count_inside_assigned
        )
        if track_count_inside == 0:
            percentage_inside_assigned = 1.0
        else:
            percentage_inside_assigned = (
                track_count_inside_assigned / track_count_inside
            )
        return TrackStatistics(
            track_count,
            track_count_outside,
            track_count_inside,
            track_count_inside_not_intersecting,
            track_count_inside_intersecting_but_unassigned,
            track_count_inside_assigned,
            percentage_inside_assigned,
        )
