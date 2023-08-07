from datetime import datetime
from typing import Iterable, Optional

from OTAnalytics.application.analysis.intersect import RunIntersect
from OTAnalytics.application.analysis.traffic_counting import RoadUserAssigner
from OTAnalytics.application.application import IntersectTracksWithSections
from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import FlowState, SectionState, TrackViewState
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.track import Track, TrackId, TrackIdProvider, TrackRepository


class SimpleIntersectTracksWithSections(IntersectTracksWithSections):
    """Intersect tracks with sections and add all intersection events in the repository.
    Args:
        intersect (RunIntersect): intersector to intersect tracks with sections
        datastore (Datastore): the datastore containing tracks, sections and events
    """

    def __init__(
        self,
        intersect: RunIntersect,
        datastore: Datastore,
    ) -> None:
        self._intersect = intersect
        self._datastore = datastore

    def run(self) -> None:
        """Runs the intersection of tracks with sections in the repository."""
        sections = self._datastore.get_all_sections()
        if not sections:
            return
        tracks = self._datastore.get_all_tracks()
        events = self._intersect.run(tracks, sections)
        self._datastore.add_events(events)


class TracksIntersectingSelectedSections(TrackIdProvider):
    """Returns track ids intersecting selected sections.
    Args:
        section_state (SectionState): the section state
        event_repository (EventRepository): the event repository
    """

    def __init__(
        self,
        section_state: SectionState,
        event_repository: EventRepository,
    ) -> None:
        self._section_state = section_state
        self._event_repository = event_repository

    def get_ids(self) -> Iterable[TrackId]:
        intersecting_ids: set[TrackId] = set()

        currently_selected_sections = self._section_state.selected_sections.get()
        for section_id in currently_selected_sections:
            for event in self._event_repository.get_all():
                if event.section_id == section_id:
                    intersecting_ids.add(TrackId(event.road_user_id))
        return intersecting_ids


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
            track_ids = self._other.get_ids()

            tracks: list[Track] = []
            for track_id in track_ids:
                if track := self._track_repository.get_for(track_id):
                    tracks.append(track)
        else:
            tracks = self._track_repository.get_all()

        return self._filter(tracks)

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
                        track.detections[0].occurrence,
                        track.detections[-1].occurrence,
                    )
                ]
            case (None, datetime() as end_date_filter):
                return [
                    track.id
                    for track in tracks
                    if self._has_overlap(
                        datetime.min,
                        end_date_filter,
                        track.detections[0].occurrence,
                        track.detections[-1].occurrence,
                    )
                ]
            case (datetime() as start_date_filter, None):
                return [
                    track.id
                    for track in tracks
                    if self._has_overlap(
                        start_date_filter,
                        datetime.max,
                        track.detections[0].occurrence,
                        track.detections[-1].occurrence,
                    )
                ]
            case _:
                return [track.id for track in tracks]

    @staticmethod
    def _has_overlap(
        start_1: datetime, end_1: datetime, start_2: datetime, end_2: datetime
    ) -> bool:
        latest_start = max(start_1, start_2)
        earliest_end = min(end_1, end_2)

        return latest_start <= earliest_end
