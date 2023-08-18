from unittest.mock import Mock

from OTAnalytics.application.analysis.traffic_counting import (
    EventPair,
    RoadUserAssigner,
    RoadUserAssignment,
    RoadUserAssignments,
)
from OTAnalytics.application.state import FlowState, ObservableProperty, SectionState
from OTAnalytics.application.use_cases.highlight_intersections import (
    TracksAssignedToSelectedFlows,
    TracksIntersectingSelectedSections,
    TracksNotIntersectingSelection,
)
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import Track, TrackId, TrackIdProvider, TrackRepository


class TestTracksIntersectingSelectedSections:
    def test_get_ids(self) -> None:
        section_id = Mock(spec=SectionId)
        event = Mock(spec=Event)
        event.section_id = section_id
        event.road_user_id = 2

        section_state = Mock(spec=SectionState)
        selected_sections = Mock(spec=ObservableProperty)
        selected_sections.get.return_value = [section_id]
        section_state.selected_sections = selected_sections

        event_repository = Mock(spec=EventRepository)
        event_repository.get_all.return_value = [event]

        tracks_intersecting_sections = TracksIntersectingSelectedSections(
            section_state, event_repository
        )
        track_ids = list(tracks_intersecting_sections.get_ids())

        assert track_ids == [TrackId(2)]
        section_state.selected_sections.get.assert_called_once()
        event_repository.get_all.assert_called_once()


class TestTracksNotIntersectingSelection:
    def test_get_ids(self) -> None:
        first_track_id = TrackId(1)
        second_track_id = TrackId(2)
        first_track = Mock(spec=Track)
        first_track.id = first_track_id
        second_track = Mock(spec=Track)
        second_track.id = second_track_id
        track_repository = Mock(spec=TrackRepository)
        track_repository.get_all.return_value = [first_track, second_track]

        tracks_intersecting_sections = Mock(spec=TrackIdProvider)
        tracks_intersecting_sections.get_ids.return_value = {first_track_id}

        tracks_not_intersecting_sections = TracksNotIntersectingSelection(
            tracks_intersecting_sections, track_repository
        )
        track_ids = list(tracks_not_intersecting_sections.get_ids())

        assert track_ids == [second_track_id]
        track_repository.get_all.assert_called_once()
        tracks_intersecting_sections.get_ids.assert_called_once()

    def test_no_selection_returns_all_tracks(self) -> None:
        first_track_id = TrackId(1)
        second_track_id = TrackId(2)
        first_track = Mock(spec=Track)
        first_track.id = first_track_id
        second_track = Mock(spec=Track)
        second_track.id = second_track_id
        track_repository = Mock(spec=TrackRepository)
        track_repository.get_all.return_value = [first_track, second_track]

        tracks_intersecting_sections = Mock(spec=TrackIdProvider)
        tracks_intersecting_sections.get_ids.return_value = {}

        tracks_not_intersecting_sections = TracksNotIntersectingSelection(
            tracks_intersecting_sections, track_repository
        )
        track_ids = list(tracks_not_intersecting_sections.get_ids())

        assert track_ids == [first_track_id, second_track_id]
        track_repository.get_all.assert_called_once()
        tracks_intersecting_sections.get_ids.assert_called_once()


class TestTracksAssignedToSelectedFlows:
    def test_get_ids(self) -> None:
        first_flow_id = FlowId("North-South")
        first_flow = Mock(spec=Flow)
        first_flow.id = first_flow_id

        second_flow_id = FlowId("North-West")
        second_flow = Mock(spec=Flow)
        second_flow.id = second_flow_id

        selected_flows = Mock(spec=ObservableProperty)
        selected_flows.get.return_value = [first_flow_id]
        flow_state = Mock(spec=FlowState)
        flow_state.selected_flows = selected_flows

        first_assignment = RoadUserAssignment(1, first_flow, Mock(spec=EventPair))
        second_assignment = RoadUserAssignment(2, second_flow, Mock(spec=EventPair))
        assignments = Mock(spec=RoadUserAssignments)
        assignments.as_list.return_value = [first_assignment, second_assignment]
        assigner = Mock(spec=RoadUserAssigner)
        assigner.assign.return_value = assignments

        event = Mock(spec=Event)
        event_repository = Mock(spec=EventRepository)
        event_repository.get_all.return_value = [event]

        flow_repository = Mock(spec=FlowRepository)
        flow_repository.get_all.return_value = [first_flow, second_flow]

        tracks_assigned_to_flow = TracksAssignedToSelectedFlows(
            assigner, event_repository, flow_repository, flow_state
        )
        track_ids = list(tracks_assigned_to_flow.get_ids())

        assert track_ids == [TrackId(1)]
        event_repository.get_all.assert_called_once()
        flow_repository.get_all.assert_called_once()
        assert selected_flows.get.call_count == 2
        assigner.assign.assert_called_once_with([event], [first_flow, second_flow])
        assignments.as_list.assert_called_once()
