from typing import Iterable

from OTAnalytics.application.analysis.intersect import TracksIntersectingSections
from OTAnalytics.application.analysis.traffic_counting import RoadUserAssigner
from OTAnalytics.application.state import FlowState, SectionState
from OTAnalytics.application.use_cases.section_repository import GetSectionsById
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.track import TrackId, TrackIdProvider, TrackRepository


class TracksIntersectingSelectedSections(TrackIdProvider):
    """Returns track ids intersecting selected sections.
    Args:
        section_state (SectionState): the section state
        tracks_intersecting_sections (TracksIntersectingSections): get track ids
            intersecting sections
        get_section_by_id (GetSectionsById): use case to get sections by id
    """

    def __init__(
        self,
        section_state: SectionState,
        tracks_intersecting_sections: TracksIntersectingSections,
        get_section_by_id: GetSectionsById,
    ) -> None:
        self._section_state = section_state
        self._tracks_intersecting_sections = tracks_intersecting_sections
        self._get_section_by_id = get_section_by_id

    def get_ids(self) -> set[TrackId]:
        currently_selected_sections = self._section_state.selected_sections.get()
        sections = self._get_section_by_id(currently_selected_sections)

        return self._tracks_intersecting_sections(sections)


class TracksNotIntersectingSelection(TrackIdProvider):
    """Returns track ids that are not intersecting the current selection sections.
    Args:
        track_id_provider (TrackIdProvider): tracks intersecting the current selection
        track_repository (EventRepository): the track repository
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
        assigner (RoadUserAssigner): to assign tracks to flows
        event_repository (EventRepository): the event repository
        flow_repository (FlowRepository): the track repository
        flow_state (FlowState): the currently selected flows
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
        return ids
