from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.analysis.intersect import RunIntersect
from OTAnalytics.application.config import CLI_CUTTING_SECTION_MARKER
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.use_cases.create_events import (
    CreateEvents,
    CreateIntersectionEvents,
    CreateSceneEvents,
    FilterOutCuttingSections,
    SectionProvider,
    SimpleCreateIntersectionEvents,
    SimpleCreateSceneEvents,
)
from OTAnalytics.application.use_cases.event_repository import AddEvents, ClearAllEvents
from OTAnalytics.application.use_cases.track_repository import GetAllTracks
from OTAnalytics.domain.event import Event
from OTAnalytics.domain.section import Section, SectionId, SectionType
from OTAnalytics.domain.track import Track
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset


@pytest.fixture
def track() -> Mock:
    return Mock(spec=Track)


@pytest.fixture
def section() -> Mock:
    section = Mock(spec=Section)
    section.id = SectionId("section")
    return section


@pytest.fixture
def event() -> Mock:
    return Mock(spec=Event)


class TestSimpleCreateIntersectionEvents:
    def test_intersection_event_creation(self, section: Mock, event: Mock) -> None:
        section_provider = Mock(spec=SectionProvider)
        provided_sections = [section]
        section_provider.return_value = provided_sections

        run_intersect = Mock(spec=RunIntersect)
        run_intersect.return_value = [event]

        add_events = Mock(spec=AddEvents)

        create_intersections_events = SimpleCreateIntersectionEvents(
            run_intersect, section_provider, add_events
        )
        create_intersections_events()

        section_provider.assert_called_once()
        run_intersect.assert_called_once_with(provided_sections)
        add_events.assert_called_once()
        assert add_events.call_args == call([event], [section.id])

    def test_empty_section_repository_should_not_run_intersection(self) -> None:
        section_provider = Mock(spec=SectionProvider)
        section_provider.return_value = []

        run_intersect = Mock(spec=RunIntersect)
        add_events = Mock(spec=AddEvents)

        create_intersections_events = SimpleCreateIntersectionEvents(
            run_intersect, section_provider, add_events
        )
        create_intersections_events()

        section_provider.assert_called_once()
        run_intersect.assert_not_called()
        add_events.assert_not_called()


class TestSimpleCreateSceneEvents:
    def test_create_scene_events(self, event: Mock) -> None:
        dataset = Mock(spec=TrackDataset)
        get_all_tracks = Mock(spec=GetAllTracks)
        get_all_tracks.as_dataset.return_value = dataset

        scene_action_detector = Mock(spec=SceneActionDetector)
        scene_action_detector.detect.return_value = [event]
        add_events = Mock(spec=AddEvents)

        create_scene_events = SimpleCreateSceneEvents(
            get_all_tracks, scene_action_detector, add_events
        )
        create_scene_events()

        get_all_tracks.as_dataset.assert_called_once()
        scene_action_detector.detect.assert_called_once_with(dataset)
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

        create_intersection_events.assert_called_once()
        create_scene_events.assert_called_once()


class TestFilterOutCuttingSections:
    def create_section(self, section_type: SectionType, name: str) -> Section:
        section = Mock(spec=Section)
        section.get_type.return_value = section_type
        section.name = name
        return section

    @pytest.fixture
    def sections(self) -> list[Section]:
        return [
            self.create_section(SectionType.LINE, "line_section"),
            self.create_section(SectionType.CUTTING, "cutting_section"),
            self.create_section(SectionType.AREA, "area_section"),
            self.create_section(
                SectionType.LINE, f"{CLI_CUTTING_SECTION_MARKER}_cli_cutting_section"
            ),
        ]

    @pytest.fixture
    def section_provider(self, sections: list[Section]) -> Mock:
        provider = Mock(spec=SectionProvider)
        provider.return_value = sections
        return provider

    def test_filter_out_cutting_sections(self, section_provider: Mock) -> None:
        _filter = FilterOutCuttingSections(section_provider)
        result = _filter.filter()

        assert len(result) == 2
        assert result[0].get_type() == SectionType.LINE
        assert result[0].name == "line_section"
        assert result[1].get_type() == SectionType.AREA
        assert result[1].name == "area_section"
        section_provider.assert_called_once()
