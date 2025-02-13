from abc import ABC
from datetime import datetime
from typing import Iterable, Optional

from OTAnalytics.application.analysis.intersect import TracksIntersectingSections
from OTAnalytics.application.analysis.traffic_counting import RoadUserAssigner
from OTAnalytics.application.state import FlowState, SectionState, TrackViewState
from OTAnalytics.application.use_cases.section_repository import (
    GetAllSections,
    GetCuttingSections,
    GetSectionsById,
)
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowId, FlowRepository
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import Track, TrackId, TrackIdProvider
from OTAnalytics.domain.track_repository import TrackRepository


class IntersectionRepository(ABC):
    def store(self, intersections: dict[SectionId, set[TrackId]]) -> None:
        raise NotImplementedError

    def get(self, sections: set[SectionId]) -> dict[SectionId, set[TrackId]]:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def remove(self, sections: set[SectionId]) -> None:
        raise NotImplementedError


class TracksIntersectingSelectedSections(TrackIdProvider):
    """Returns track ids intersecting selected sections.

    Args:
        section_state (SectionState): the section state.
        tracks_intersecting_sections (TracksIntersectingSections): get track ids
            intersecting sections.
        get_section_by_id (GetSectionsById): use case to get sections by id.
    """

    def __init__(
        self,
        section_state: SectionState,
        tracks_intersecting_sections: TracksIntersectingSections,
        get_section_by_id: GetSectionsById,
        intersection_repository: IntersectionRepository,
    ) -> None:
        self._section_state = section_state
        self._tracks_intersecting_sections = tracks_intersecting_sections
        self._get_section_by_id = get_section_by_id
        self._intersection_repository = intersection_repository

    def get_ids(self) -> set[TrackId]:
        currently_selected_sections = self._section_state.selected_sections.get()
        return TracksIntersectingGivenSections(
            set(currently_selected_sections),
            self._tracks_intersecting_sections,
            self._get_section_by_id,
            self._intersection_repository,
        ).get_ids()


class TracksIntersectingAllNonCuttingSections(TrackIdProvider):
    """Returns track ids intersecting all sections which are not a cutting section.

    Args:
        get_all_sections (GetAllSections): the use case to get all sections.
        tracks_intersecting_sections (TracksIntersectingSections): get track ids
            intersecting sections.
        get_sections_by_id (GetSectionsById): use case to get sections by id.
    """

    def __init__(
        self,
        get_cutting_sections: GetCuttingSections,
        get_all_sections: GetAllSections,
        tracks_intersecting_sections: TracksIntersectingSections,
        get_sections_by_id: GetSectionsById,
        intersection_repository: IntersectionRepository,
    ) -> None:
        self._get_cutting_sections = get_cutting_sections
        self._get_all_sections = get_all_sections
        self._tracks_intersecting_sections = tracks_intersecting_sections
        self._get_section_by_id = get_sections_by_id
        self._intersection_repository = intersection_repository

    def get_ids(self) -> set[TrackId]:
        ids_non_cutting_sections = {
            section.id
            for section in self._get_all_sections()
            if section not in self._get_cutting_sections()
        }
        return TracksIntersectingGivenSections(
            ids_non_cutting_sections,
            self._tracks_intersecting_sections,
            self._get_section_by_id,
            self._intersection_repository,
        ).get_ids()


class TracksIntersectingAllSections(TrackIdProvider):
    """Returns track ids intersecting all sections.

    Args:
        get_all_sections (GetAllSections): the use case to get all sections.
        tracks_intersecting_sections (TracksIntersectingSections): get track ids
            intersecting sections.
        get_section_by_id (GetSectionsById): use case to get sections by id.
    """

    def __init__(
        self,
        get_all_sections: GetAllSections,
        tracks_intersecting_sections: TracksIntersectingSections,
        get_section_by_id: GetSectionsById,
        intersection_repository: IntersectionRepository,
    ) -> None:
        self._get_all_sections = get_all_sections
        self._tracks_intersecting_sections = tracks_intersecting_sections
        self._get_section_by_id = get_section_by_id
        self._intersection_repository = intersection_repository

    def get_ids(self) -> set[TrackId]:
        ids_all_sections = {section.id for section in self._get_all_sections()}
        return TracksIntersectingGivenSections(
            ids_all_sections,
            self._tracks_intersecting_sections,
            self._get_section_by_id,
            self._intersection_repository,
        ).get_ids()


class TracksIntersectingGivenSections(TrackIdProvider):
    """Returns track ids intersecting given sections.

    Args:
        section_ids (list[SectionId]): the sections to identify intersection tracks.
        tracks_intersecting_sections (TracksIntersectingSections): get track ids
            intersecting sections.
        get_section_by_id (GetSectionsById): use case to get sections by id.
    """

    def __init__(
        self,
        section_ids: set[SectionId],
        tracks_intersecting_sections: TracksIntersectingSections,
        get_section_by_id: GetSectionsById,
        intersection_repository: IntersectionRepository,
    ) -> None:
        self._section_ids = section_ids
        self._tracks_intersecting_sections = tracks_intersecting_sections
        self._get_section_by_id = get_section_by_id
        self._intersection_repository = intersection_repository

    def get_ids(self) -> set[TrackId]:
        existing_intersections = self._intersection_repository.get(self._section_ids)
        section_ids_to_process = self._section_ids - existing_intersections.keys()
        new_intersections = self._calculate_new_intersections(section_ids_to_process)
        return set.union(new_intersections, *existing_intersections.values())

    def _calculate_new_intersections(
        self, section_ids_to_process: set[SectionId]
    ) -> set[TrackId]:
        new_intersections: set[TrackId] = set()
        if section_ids_to_process:
            sections = self._get_section_by_id(section_ids_to_process)
            intersections = self._tracks_intersecting_sections(sections)
            self._intersection_repository.store(intersections)
            new_intersections.update(*intersections.values())
        return new_intersections


class TracksNotIntersectingSelection(TrackIdProvider):
    """Returns track ids that are not intersecting the current selection sections.

    Args:
        track_id_provider (TrackIdProvider): tracks intersecting the current selection.
        track_repository (EventRepository): the track repository.
    """

    def __init__(
        self,
        track_id_provider: TrackIdProvider,
        track_repository: TrackRepository,
    ) -> None:
        self._track_id_provider = track_id_provider
        self._track_repository = track_repository

    def get_ids(self) -> Iterable[TrackId]:
        all_track_ids = {track.id for track in self._track_repository.get_all()}
        assigned_tracks = set(self._track_id_provider.get_ids())
        return all_track_ids - assigned_tracks


class TracksAssignedToSelectedFlows(TrackIdProvider):
    """Returns track ids that are assigned to the currently selected flows.

    Args:
        assigner (RoadUserAssigner): to assign tracks to flows.
        event_repository (EventRepository): the event repository.
        flow_repository (FlowRepository): the track repository.
        flow_state (FlowState): the currently selected flows.
    """

    def __init__(
        self,
        assigner: RoadUserAssigner,
        event_repository: EventRepository,
        flow_repository: FlowRepository,
        flow_state: FlowState,
    ) -> None:
        self._assigner = assigner
        self._event_repository = event_repository
        self._flow_repository = flow_repository
        self._flow_state = flow_state

    def get_ids(self) -> Iterable[TrackId]:
        events = self._event_repository.get_all()
        # All flows must be passed to assigner to ensure that a track potentially
        # belonging to several flows is assigned to the correct one.
        all_flows = self._flow_repository.get_all()
        assignments = self._assigner.assign(events, all_flows).as_list()

        ids = set()
        for assignment in assignments:
            if assignment.assignment.id in self._flow_state.selected_flows.get():
                ids.add(TrackId(assignment.road_user))
        print(f"Tracks assigned to selected flow(s): {len(ids)}")
        return ids


class TracksAssignedToAllFlows(TrackIdProvider):
    """Returns track ids that are assigned to all flows.

    Args:
        assigner (RoadUserAssigner): to assign tracks to flows.
        event_repository (EventRepository): the event repository.
        flow_repository (FlowRepository): the track repository.
    """

    def __init__(
        self,
        assigner: RoadUserAssigner,
        event_repository: EventRepository,
        flow_repository: FlowRepository,
    ) -> None:
        self._assigner = assigner
        self._event_repository = event_repository
        self._flow_repository = flow_repository

    def get_ids(self) -> Iterable[TrackId]:
        all_flow_ids = [flow.id for flow in self._flow_repository.get_all()]
        return TracksAssignedToGivenFlows(
            self._assigner, self._event_repository, self._flow_repository, all_flow_ids
        ).get_ids()


class TracksAssignedToGivenFlows(TrackIdProvider):
    """Returns track ids that are assigned to the given flows.

    Args:
        assigner (RoadUserAssigner): to assign tracks to flows.
        event_repository (EventRepository): the event repository.
        flow_repository (FlowRepository): the track repository.
        flow_ids (list[FlowId]): the flows to identify assigned tracks for.
    """

    def __init__(
        self,
        assigner: RoadUserAssigner,
        event_repository: EventRepository,
        flow_repository: FlowRepository,
        flow_ids: list[FlowId],
    ) -> None:
        self._assigner = assigner
        self._event_repository = event_repository
        self._flow_repository = flow_repository
        self._flows = list(flow_ids)

    def get_ids(self) -> Iterable[TrackId]:
        events = self._event_repository.get_all()
        # All flows must be passed to assigner to ensure that a track potentially
        # belonging to several flows is assigned to the correct one.
        all_flows = self._flow_repository.get_all()
        assignments = self._assigner.assign(events, all_flows).as_list()

        ids = set()
        for assignment in assignments:
            if assignment.assignment.id in self._flows:
                ids.add(TrackId(assignment.road_user))
        return ids


class TracksOverlapOccurrenceWindow(TrackIdProvider):
    def __init__(
        self,
        track_repository: TrackRepository,
        track_view_state: TrackViewState,
        other: Optional[TrackIdProvider] = None,
    ) -> None:
        """Returns track ids that overlap with the current date range filter.

        Args:
            track_repository (TrackRepository): the track repository.
            track_view_state (TrackViewState): contains information of current
                filter element.
            other (Optional[TrackIdProvider], optional): Takes ids of others for
                filtering. Defaults to None.
        """
        self._other = other
        self._track_repository = track_repository
        self._track_view_state = track_view_state

    def get_ids(self) -> Iterable[TrackId]:
        if self._other:
            tracks = self._get_other_track_ids()
        else:
            tracks = self._track_repository.get_all()

        return self._filter(tracks)

    def _get_other_track_ids(self) -> Iterable[Track]:
        if self._other:
            track_ids = self._other.get_ids()
            tracks: list[Track] = []
            for track_id in track_ids:
                if track := self._track_repository.get_for(track_id):
                    tracks.append(track)
            return tracks
        return []

    def _filter(self, tracks: Iterable[Track]) -> Iterable[TrackId]:
        date_range = self._track_view_state.filter_element.get().date_range
        start_date_filter = date_range.start_date
        end_date_filter = date_range.end_date

        match (start_date_filter, end_date_filter):
            case (datetime() as start_date_filter, datetime() as end_date_filter):
                return [
                    track.id
                    for track in tracks
                    if self._has_overlap(
                        start_date_filter,
                        end_date_filter,
                        track.start,
                        track.end,
                    )
                ]
            case (None, datetime() as end_date_filter):
                return [
                    track.id
                    for track in tracks
                    if self._has_overlap(
                        datetime.min,
                        end_date_filter,
                        track.start,
                        track.end,
                    )
                ]
            case (datetime() as start_date_filter, None):
                return [
                    track.id
                    for track in tracks
                    if self._has_overlap(
                        start_date_filter,
                        datetime.max,
                        track.start,
                        track.end,
                    )
                ]
            case _:
                return [track.id for track in tracks]

    @staticmethod
    def _has_overlap(
        start_1: datetime, end_1: datetime, start_2: datetime, end_2: datetime
    ) -> bool:
        if not start_1 <= end_1:
            raise ValueError("start_1 needs to be lesser equal than end_1.")
        if not start_2 <= end_2:
            raise ValueError("start_2 needs to be lesser equal than end_2.")
        latest_start = max(start_1, start_2)
        earliest_end = min(end_1, end_2)

        return latest_start <= earliest_end
