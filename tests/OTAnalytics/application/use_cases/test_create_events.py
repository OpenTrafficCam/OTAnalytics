from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.analysis.intersect import RunIntersect
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.use_cases.create_events import (
    CreateEvents,
    CreateIntersectionEvents,
    CreateSceneEvents,
    SimpleCreateIntersectionEvents,
    SimpleCreateSceneEvents,
)
from OTAnalytics.application.use_cases.event_repository import AddEvents, ClearAllEvents
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.section import Section, SectionRepository
from OTAnalytics.domain.track import Track


@pytest.fixture
def track() -> Mock:
    return Mock(spec=Track)


@pytest.fixture
def section() -> Mock:
    return Mock(spec=Section)


@pytest.fixture
def event() -> Mock:
    return Mock(spec=Event)


class TestSimpleCreateIntersectionEvents:
    def test_intersection_event_creation(self, section: Mock, event: Mock) -> None:
        section_repository = Mock(spec=SectionRepository)
        section_repository.get_all.return_value = [section]

        run_intersect = Mock(spec=RunIntersect)
        run_intersect.return_value = [event]

        add_events = Mock(spec=AddEvents)

        create_intersections_events = SimpleCreateIntersectionEvents(
            run_intersect, section_repository, add_events
        )
        create_intersections_events()

        section_repository.get_all.assert_called_once()
        run_intersect.assert_called_once_with([section])
        add_events.assert_called_once_with([event])

    def test_empty_section_repository_should_not_run_intersection(self) -> None:
        section_repository = Mock(spec=SectionRepository)
        section_repository.get_all.return_value = []

        run_intersect = Mock(spec=RunIntersect)
        add_events = Mock(spec=AddEvents)

        create_intersections_events = SimpleCreateIntersectionEvents(
            run_intersect, section_repository, add_events
        )
        create_intersections_events()

        section_repository.get_all.assert_called_once()
        run_intersect.assert_not_called()
        add_events.assert_not_called()


class TestSimpleCreateSceneEvents:
    def test_create_scene_events(self, track: Mock, event: Mock) -> None:
        get_all_tracks = Mock(spec=GetAllTracks)
        get_all_tracks.return_value = [track]

        scene_action_detector = Mock(spec=SceneActionDetector)
        scene_action_detector.detect.return_value = [event]
        add_events = Mock(spec=AddEvents)

        create_scene_events = SimpleCreateSceneEvents(
            get_all_tracks, scene_action_detector, add_events
        )
        create_scene_events()

        get_all_tracks.assert_called_once()
        scene_action_detector.detect.assert_called_once_with([track])
        add_events.assert_called_once_with([event])


class TestCreateEvents:
    def test_create_events(self) -> None:
        clear_all_events = Mock(spec=ClearAllEvents)
        create_intersection_events = Mock(spec=CreateIntersectionEvents)
        create_scene_events = Mock(spec=CreateSceneEvents)

        create_events = CreateEvents(
            clear_all_events, create_intersection_events, create_scene_events
        )

        method_execution_order_observer = Mock()
        method_execution_order_observer.configure_mock(
            clear_event_repository=clear_all_events,
            create_intersection_events=create_intersection_events,
            create_scene_events=create_scene_events,
        )

        create_events()

        clear_all_events.assert_called_once()
        create_intersection_events.assert_called_once()
        create_scene_events.assert_called_once()

        # Check that clearing event repository is called first
        method_execution_order_observer.mock_calls == [
            call.clear_event_repository(),
            call.create_intersection_events(),
            call.create_scene_events(),
        ]
