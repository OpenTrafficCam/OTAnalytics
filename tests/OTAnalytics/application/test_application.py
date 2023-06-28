from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.analysis.intersect import RunIntersect
from OTAnalytics.application.application import (
    AddFlow,
    AddSection,
    ClearEventRepository,
    FlowAlreadyExists,
    IntersectTracksWithSections,
    SectionAlreadyExists,
    TracksIntersectingSelectedSections,
)
from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import ObservableProperty, SectionState
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.flow import Flow, FlowRepository
from OTAnalytics.domain.section import Section, SectionId, SectionRepository
from OTAnalytics.domain.track import Track, TrackId


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
        assert datastore.add_events.call_args_list == [call([event])]


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
