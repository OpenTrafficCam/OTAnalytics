from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.state import SectionState, TrackObserver, TrackState
from OTAnalytics.domain.section import SectionId, SectionObserver
from OTAnalytics.domain.track import TrackId


class TestTrackState:
    def test_notify_observer(self) -> None:
        first_track = TrackId(1)
        changed_track = TrackId(2)
        observer = Mock(spec=TrackObserver)
        state = TrackState()
        state.register(observer)

        state.select(first_track)
        state.select(changed_track)
        state.select(changed_track)

        assert observer.notify_track.call_args_list == [
            call(first_track),
            call(changed_track),
        ]

    def test_update_selected_track_on_notify_tracks(self) -> None:
        first_track = TrackId(1)
        second_track = TrackId(2)
        state = TrackState()

        state.notify_tracks([first_track, second_track])

        assert state.selected_track == first_track

    def test_update_selected_track_on_notify_tracks_with_empty_list(self) -> None:
        with pytest.raises(IndexError):
            TrackState().notify_tracks([])


class TestSectionState:
    def test_notify_observer(self) -> None:
        first_section = SectionId("north")
        changed_section = SectionId("south")
        observer = Mock(spec=SectionObserver)
        state = SectionState()
        state.register(observer)

        state.select(first_section)
        state.select(changed_section)
        state.select(changed_section)

        assert observer.notify_section.call_args_list == [
            call(first_section),
            call(changed_section),
        ]

    def test_update_selected_section_on_notify_sections(self) -> None:
        first = SectionId("north")
        second = SectionId("south")
        state = SectionState()

        state.notify_sections([first, second])

        assert state.selected_section == first

    def test_update_selected_section_on_notify_sections_with_empty_list(self) -> None:
        with pytest.raises(IndexError):
            SectionState().notify_sections([])
