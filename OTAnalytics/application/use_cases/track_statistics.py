from dataclasses import dataclass

from domain.section import Section

from OTAnalytics.application.use_cases.highlight_intersections import (
    TracksAssignedToAllFlows,
    TracksIntersectingAllSections,
    TracksIntersectingGivenSections,
    TracksNotIntersectingGivenSections,
)
from OTAnalytics.domain.track_repository import TrackRepository

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
        track_repository: TrackRepository,
    ) -> None:
        self._intersection_all_section = intersection_all_sections
        self._assigned_to_all_flows = assigned_to_all_flows
        self._track_repository = track_repository

    def get_statistics(self) -> TrackStatistics:
        self.update_track_count_inside()
        self.update_track_count_outside()
        track_count_inside = len(self._inside_cutting_section.get_ids())
        track_count_outside = len(self._outside_cutting_section.get_ids())
        track_count = track_count_inside + track_count_outside
        track_count_inside_not_intersecting = len(
            self._inside_cutting_section.get_ids().difference(
                self._intersection_all_section.get_ids()
            )
        )
        track_count_inside_assigned = len(
            self._inside_cutting_section.get_ids().intersection(
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

    def get_cutting_section_id_set(self) -> set[Section]:
        cutting_section_id_set = set()
        for section in self._intersection_all_section._get_all_sections():
            if section.name.startswith(START_OF_CUTTING_SECTION_NAME):
                cutting_section_id_set.add(section.id)
                break
        return cutting_section_id_set

    def update_track_count_inside(self) -> None:
        self._inside_cutting_section = TracksIntersectingGivenSections(
            self.get_cutting_section_id_set(),
            self._intersection_all_section._tracks_intersecting_sections,
            self._intersection_all_section._get_section_by_id,
            self._intersection_all_section._intersection_repository,
        )

    def update_track_count_outside(self) -> None:
        self._outside_cutting_section = TracksNotIntersectingGivenSections(
            self.get_cutting_section_id_set(),
            self._intersection_all_section._tracks_intersecting_sections,
            self._intersection_all_section._get_section_by_id,
            self._intersection_all_section._intersection_repository,
            self._track_repository,
        )
