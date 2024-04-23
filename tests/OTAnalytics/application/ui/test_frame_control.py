from datetime import datetime, timedelta
from unittest.mock import Mock

import pytest

from OTAnalytics.application.playback import SkipTime
from OTAnalytics.application.state import SectionState, TrackViewState, VideosMetadata
from OTAnalytics.application.ui.frame_control import (
    SwitchToEvent,
    SwitchToNext,
    SwitchToPrevious,
)
from OTAnalytics.application.use_cases.filter_visualization import (
    CreateDefaultFilterRange,
)
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.event import Event, EventRepository
from OTAnalytics.domain.filter import FilterElement
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.types import EventType
from OTAnalytics.domain.video import VideoMetadata
from tests.utils.state import observable

FPS = 1
TIME_OF_A_FRAME = timedelta(seconds=1) / FPS
START_DATE = datetime(2023, 1, 1, 0, 0, 0)
END_DATE = datetime(2023, 1, 1, 0, 0, 1)
FILTER_DURATION = END_DATE - START_DATE
EVENT_OCCURRENCE = END_DATE + timedelta(seconds=1)


@pytest.fixture
def filter_element() -> Mock:
    filter_element = Mock(spec=FilterElement)
    filter_element.date_range = DateRange(START_DATE, END_DATE)
    return filter_element


@pytest.fixture
def skip_time() -> Mock:
    skip_time = Mock(spec=SkipTime)
    skip_time.seconds = 0
    skip_time.frames = 1
    return skip_time


@pytest.fixture
def track_view_state(filter_element: Mock, skip_time: Mock) -> Mock:
    track_view_state = Mock(spec=TrackViewState)
    track_view_state.filter_element = observable(filter_element)
    track_view_state.skip_time = observable(skip_time)
    return track_view_state


@pytest.fixture
def section_state() -> Mock:
    selected_section = SectionId("selected section")
    section_state = Mock(spec=SectionState)
    section_state.selected_sections = observable([selected_section])
    return section_state


@pytest.fixture
def videos_metadata() -> VideosMetadata:
    metadata = Mock(spec=VideoMetadata)
    metadata.fps = FPS
    videos_metadata = Mock(spec=VideosMetadata)
    videos_metadata.get_metadata_for.return_value = metadata
    return videos_metadata


class TestSwitchToNextFrame:
    def test_set_next_frame(
        self,
        track_view_state: Mock,
        videos_metadata: Mock,
        filter_element: Mock,
    ) -> None:
        create_default_filter = Mock(spec=CreateDefaultFilterRange)
        derived_filter_element = Mock(spec=FilterElement)
        filter_element.derive_date.return_value = derived_filter_element

        new_date_range = DateRange(
            START_DATE + TIME_OF_A_FRAME, END_DATE + TIME_OF_A_FRAME
        )
        use_case = SwitchToNext(
            track_view_state, videos_metadata, create_default_filter
        )

        use_case.switch_frame()

        filter_element.derive_date.assert_called_with(new_date_range)
        track_view_state.filter_element.set.assert_called_with(derived_filter_element)
        videos_metadata.get_metadata_for.assert_called_with(END_DATE)
        create_default_filter.create.assert_called_once()


class TestSwitchToPreviousFrame:
    def test_set_next_frame(
        self,
        track_view_state: Mock,
        videos_metadata: Mock,
        filter_element: Mock,
    ) -> None:
        create_default_filter = Mock(spec=CreateDefaultFilterRange)
        derived_filter_element = Mock(spec=FilterElement)
        filter_element.derive_date.return_value = derived_filter_element

        new_date_range = DateRange(
            START_DATE - TIME_OF_A_FRAME, END_DATE - TIME_OF_A_FRAME
        )
        use_case = SwitchToPrevious(
            track_view_state, videos_metadata, create_default_filter
        )

        use_case.switch_frame()

        filter_element.derive_date.assert_called_with(new_date_range)
        track_view_state.filter_element.set.assert_called_with(derived_filter_element)
        videos_metadata.get_metadata_for.assert_called_with(END_DATE)
        create_default_filter.create.assert_called_once()


class TestSwitchToEvent:
    def test_switch_to_previous(
        self,
        track_view_state: Mock,
        section_state: Mock,
        filter_element: Mock,
    ) -> None:
        create_default_filter = Mock(spec=CreateDefaultFilterRange)
        derived_filter_element = Mock(spec=FilterElement)
        filter_element.derive_date.return_value = derived_filter_element
        event = Mock(spec=Event)
        event.occurrence = EVENT_OCCURRENCE
        new_date_range = DateRange(EVENT_OCCURRENCE - FILTER_DURATION, EVENT_OCCURRENCE)
        event_repository = Mock(spec=EventRepository)
        event_repository.get_previous_before.return_value = event

        use_case = SwitchToEvent(
            event_repository, track_view_state, section_state, create_default_filter
        )

        use_case.switch_to_previous()

        section_state.selected_sections.get.assert_called()
        filter_element.derive_date.assert_called_with(new_date_range)
        event_repository.get_previous_before.assert_called_with(
            date=END_DATE,
            sections=section_state.selected_sections.get(),
            event_types=(EventType.SECTION_ENTER, EventType.SECTION_LEAVE),
        )
        track_view_state.filter_element.set.assert_called_with(derived_filter_element)
        create_default_filter.create.assert_called_once()

    def test_switch_to_previous_without_next_event(
        self,
        track_view_state: Mock,
        section_state: Mock,
        filter_element: Mock,
    ) -> None:
        create_default_filter = Mock(spec=CreateDefaultFilterRange)
        derived_filter_element = Mock(spec=FilterElement)
        filter_element.derive_date.return_value = derived_filter_element
        event_repository = Mock(spec=EventRepository)
        event_repository.get_previous_before.return_value = None

        use_case = SwitchToEvent(
            event_repository, track_view_state, section_state, create_default_filter
        )

        use_case.switch_to_previous()

        section_state.selected_sections.get.assert_called()
        filter_element.derive_date.assert_not_called()
        event_repository.get_previous_before.assert_called_with(
            date=END_DATE,
            sections=section_state.selected_sections.get(),
            event_types=(EventType.SECTION_ENTER, EventType.SECTION_LEAVE),
        )
        track_view_state.filter_element.set.assert_not_called()
        create_default_filter.create.assert_called_once()

    def test_switch_to_next(
        self,
        track_view_state: Mock,
        section_state: Mock,
        filter_element: Mock,
    ) -> None:
        create_default_filter = Mock(spec=CreateDefaultFilterRange)
        derived_filter_element = Mock(spec=FilterElement)
        filter_element.derive_date.return_value = derived_filter_element
        event = Mock(spec=Event)
        event.occurrence = EVENT_OCCURRENCE
        new_date_range = DateRange(EVENT_OCCURRENCE - FILTER_DURATION, EVENT_OCCURRENCE)
        event_repository = Mock(spec=EventRepository)
        event_repository.get_next_after.return_value = event

        use_case = SwitchToEvent(
            event_repository, track_view_state, section_state, create_default_filter
        )

        use_case.switch_to_next()

        section_state.selected_sections.get.assert_called()
        filter_element.derive_date.assert_called_with(new_date_range)
        event_repository.get_next_after.assert_called_with(
            date=END_DATE,
            sections=section_state.selected_sections.get(),
            event_types=(EventType.SECTION_ENTER, EventType.SECTION_LEAVE),
        )
        track_view_state.filter_element.set.assert_called_with(derived_filter_element)
        create_default_filter.create.assert_called_once()

    def test_switch_to_next_without_next_event(
        self,
        track_view_state: Mock,
        section_state: Mock,
        filter_element: Mock,
    ) -> None:
        create_default_filter = Mock(spec=CreateDefaultFilterRange)
        derived_filter_element = Mock(spec=FilterElement)
        filter_element.derive_date.return_value = derived_filter_element
        event_repository = Mock(spec=EventRepository)
        event_repository.get_next_after.return_value = None

        use_case = SwitchToEvent(
            event_repository, track_view_state, section_state, create_default_filter
        )

        use_case.switch_to_next()

        section_state.selected_sections.get.assert_called()
        filter_element.derive_date.assert_not_called()
        event_repository.get_next_after.assert_called_with(
            date=END_DATE,
            sections=section_state.selected_sections.get(),
            event_types=(EventType.SECTION_ENTER, EventType.SECTION_LEAVE),
        )
        track_view_state.filter_element.set.assert_not_called()
        create_default_filter.create.assert_called_once()
