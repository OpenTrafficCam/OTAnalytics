from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.analysis.intersect import RunIntersect
from OTAnalytics.application.analysis.traffic_counting import (
    EventPair,
    RoadUserAssigner,
    RoadUserAssignment,
    RoadUserAssignments,
)
from OTAnalytics.application.application import (
    AddFlow,
    AddSection,
    ClearEventRepository,
    FlowAlreadyExists,
    IntersectTracksWithSections,
    SectionAlreadyExists,
    TracksAssignedToSelectedFlows,
    TracksIntersectingSelectedSections,
    TracksNotIntersectingSelection,
)
from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import FlowState, ObservableProperty, SectionState
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.flow import Flow, FlowId, FlowRepository
from OTAnalytics.domain.section import Section, SectionId, SectionRepository
from OTAnalytics.domain.track import Track, TrackId, TrackIdProvider, TrackRepository


class TestAddSection:
    def test_add_section_with_different_names(self) -> None:
        some_section = Mock(spec=Section)
        some_section.name = "some"
        other_section = Mock(spec=Section)
        other_section.name = "other"
        section_repository = Mock(spec=SectionRepository)
        section_repository.get_all.return_value = [some_section]
        use_case = AddSection(section_repository)

        use_case.add(other_section)

        assert section_repository.add.call_args_list == [
            call(other_section),
        ]

    def test_add_section_with_same_names(self) -> None:
        some_section = Mock(spec=Section)
        some_section.id = SectionId("some")
        some_section.name = "some"
        other_section = Mock(spec=Section)
        other_section.id = SectionId("other")
        other_section.name = "some"
        section_repository = Mock(spec=SectionRepository)
        section_repository.get_all.return_value = [some_section]
        use_case = AddSection(section_repository)

        with pytest.raises(SectionAlreadyExists):
            use_case.add(other_section)


class TestAddFlow:
    def test_add_flow_with_different_names(self) -> None:
        some_flow = Mock(spec=Flow)
        some_flow.name = "some"
        other_flow = Mock(spec=Flow)
        other_flow.name = "other"
        flow_repository = Mock(spec=FlowRepository)
        flow_repository.get_all.return_value = [some_flow]
        use_case = AddFlow(flow_repository)

        use_case.add(other_flow)

        assert flow_repository.add.call_args_list == [
            call(other_flow),
        ]

    def test_add_flow_with_same_names(self) -> None:
        some_flow = Mock(spec=Flow)
        some_flow.name = "some"
        other_flow = Mock(spec=Flow)
        other_flow.name = "some"
        flow_repository = Mock(spec=FlowRepository)
        flow_repository.get_all.return_value = [some_flow]
        use_case = AddFlow(flow_repository)

        with pytest.raises(FlowAlreadyExists):
            use_case.add(other_flow)


class TestClearEventRepository:
    def test_clear(self) -> None:
        repository = Mock(spec=EventRepository)
        clear_event_repository = ClearEventRepository(repository)
        clear_event_repository.clear()
        repository.clear.assert_called_once()


class TestIntersectTracksWithSections:
    def test_run(self) -> None:
        track = Mock(spec=Track)
        section = Mock(spec=Section)
        event = Mock(spec=Event)

        datastore = Mock(spec=Datastore)
        datastore.get_all_tracks.return_value = [track]
        datastore.get_all_sections.return_value = [section]

        intersect = Mock(spec=RunIntersect)
        intersect.run.return_value = [event]

        intersect_tracks_sections = IntersectTracksWithSections(intersect, datastore)
        intersect_tracks_sections.run()

        datastore.get_all_tracks.assert_called_once()
        datastore.get_all_sections.assert_called_once()

        assert intersect.run.call_args_list == [call([track], [section])]


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
