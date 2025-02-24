from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from OTAnalytics.application.use_cases.event_repository import GetAllEnterSectionEvents
from OTAnalytics.application.use_cases.number_of_tracks_to_be_validated import (
    NumberOfTracksToBeValidated,
)
from OTAnalytics.domain.track import TrackIdProvider


@dataclass
class TrackStatistics:
    track_count: int = 0
    track_count_outside: int = 0
    track_count_inside: int = 0
    track_count_inside_not_intersecting: int = 0
    track_count_inside_intersecting_but_unassigned: int = 0
    track_count_inside_assigned: int = 0
    percentage_inside_assigned: float = 1
    percentage_inside_not_intersection: float = 1
    percentage_inside_intersecting_but_unassigned: float = 1
    number_of_tracks_to_be_validated: int = 0
    number_of_tracks_with_simultaneous_section_events: int = 0

    def __add__(self, other: Any) -> "TrackStatistics":
        if not isinstance(other, TrackStatistics):
            raise TypeError(f"{type(other)} is not of type {TrackStatistics}")

        track_count_inside = self.track_count_inside + other.track_count_inside
        track_count_inside_not_intersecting = (
            self.track_count_inside_not_intersecting
            + other.track_count_inside_not_intersecting
        )
        track_count_inside_intersecting_but_unassigned = (
            self.track_count_inside_intersecting_but_unassigned
            + other.track_count_inside_intersecting_but_unassigned
        )
        track_count_inside_assigned = (
            self.track_count_inside_assigned + other.track_count_inside_assigned
        )
        return TrackStatistics(
            track_count=(self.track_count + other.track_count),
            track_count_outside=(self.track_count_outside + other.track_count_outside),
            track_count_inside=track_count_inside,
            track_count_inside_not_intersecting=track_count_inside_not_intersecting,
            track_count_inside_intersecting_but_unassigned=(
                track_count_inside_intersecting_but_unassigned
            ),
            track_count_inside_assigned=track_count_inside_assigned,
            percentage_inside_assigned=percentage(
                track_count_inside_assigned, track_count_inside
            ),
            percentage_inside_not_intersection=percentage(
                track_count_inside_not_intersecting, track_count_inside
            ),
            percentage_inside_intersecting_but_unassigned=percentage(
                track_count_inside_intersecting_but_unassigned, track_count_inside
            ),
            number_of_tracks_to_be_validated=(
                self.number_of_tracks_to_be_validated
                + other.number_of_tracks_to_be_validated
            ),
            number_of_tracks_with_simultaneous_section_events=(
                self.number_of_tracks_with_simultaneous_section_events
                + other.number_of_tracks_with_simultaneous_section_events
            ),
        )


class CalculateTrackStatistics:
    def __init__(
        self,
        intersection_all_non_cutting_sections: TrackIdProvider,
        assigned_to_all_flows: TrackIdProvider,
        all_tracks: TrackIdProvider,
        track_ids_inside_cutting_sections: TrackIdProvider,
        number_of_tracks_to_be_validated: NumberOfTracksToBeValidated,
        get_all_enter_section_events: GetAllEnterSectionEvents,
    ) -> None:
        self._intersection_all_non_cutting_sections = (
            intersection_all_non_cutting_sections
        )
        self._assigned_to_all_flows = assigned_to_all_flows
        self._all_tracks = all_tracks
        self._track_ids_inside_cutting_sections = track_ids_inside_cutting_sections
        self._number_of_tracks_to_be_validated = number_of_tracks_to_be_validated
        self._get_all_enter_section_events = get_all_enter_section_events

    def get_statistics(self) -> TrackStatistics:
        ids_all = set(self._all_tracks.get_ids())
        ids_inside_cutting_sections = set(
            self._track_ids_inside_cutting_sections.get_ids()
        )

        track_count_inside = len(ids_inside_cutting_sections)
        track_count = len(ids_all)

        track_count_outside = track_count - track_count_inside

        track_count_inside_not_intersecting = len(
            ids_inside_cutting_sections.difference(
                self._intersection_all_non_cutting_sections.get_ids()
            )
        )
        track_count_inside_assigned = len(
            ids_inside_cutting_sections.intersection(
                self._assigned_to_all_flows.get_ids()
            )
        )
        track_count_inside_intersecting_but_unassigned = (
            track_count_inside
            - track_count_inside_not_intersecting
            - track_count_inside_assigned
        )
        percentage_inside_assigned = percentage(
            track_count_inside_assigned, track_count_inside
        )
        percentage_inside_not_intersection = percentage(
            track_count_inside_not_intersecting, track_count_inside
        )
        percentage_inside_intersecting_but_unassigned = percentage(
            track_count_inside_intersecting_but_unassigned, track_count_inside
        )
        return TrackStatistics(
            track_count,
            track_count_outside,
            track_count_inside,
            track_count_inside_not_intersecting,
            track_count_inside_intersecting_but_unassigned,
            track_count_inside_assigned,
            percentage_inside_assigned,
            percentage_inside_not_intersection,
            percentage_inside_intersecting_but_unassigned,
            self._number_of_tracks_to_be_validated.calculate(),
            self.get_number_of_tracks_with_simultaneous_events(),
        )

    def get_number_of_tracks_with_simultaneous_events(self) -> int:
        # Group events by road_user_id and occurrence
        event_counts = self._count_simultaneous_events()

        # Count tracks with simultaneous events
        return sum(
            1
            for occurrences in event_counts.values()
            if any(count > 1 for count in occurrences.values())
        )

    def _count_simultaneous_events(self) -> dict[str, dict[datetime, int]]:
        """
        Count occurrences of events per road user and timestamp.
        """
        events = self._get_all_enter_section_events.get()
        event_counts: dict[str, dict[datetime, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        for event in events:
            event_counts[event.road_user_id][event.occurrence] += 1
        return event_counts


def percentage(track_count: int, all_tracks: int) -> float:
    if all_tracks == 0:
        return 1.0
    return track_count / all_tracks
