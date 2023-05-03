from datetime import datetime
from unittest.mock import Mock, call, patch

import pytest

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import (
    FilterElementState,
    ObservableProperty,
    Observer,
    Plotter,
    SectionState,
    TrackImageUpdater,
    TrackObserver,
    TrackState,
    TrackViewState,
)
from OTAnalytics.domain.filter import FilterElement
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track import Track, TrackId, TrackImage


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


class TestObservableProperty:
    def test_notify_observer(self) -> None:
        first_section = SectionId("north")
        changed_section = SectionId("south")
        observer = Mock(spec=Observer)
        state = ObservableProperty[SectionId]()
        state.register(observer)

        state.set(first_section)
        state.set(changed_section)
        state.set(changed_section)

        assert observer.call_args_list == [
            call(first_section),
            call(changed_section),
        ]

    def test_update_selected_section_on_notify_sections(self) -> None:
        first = SectionId("north")
        second = SectionId("south")
        state = SectionState()

        state.notify_sections([first, second])

        assert state.selected_section.get() == first

    def test_update_selected_section_on_notify_sections_with_empty_list(self) -> None:
        with pytest.raises(IndexError):
            SectionState().notify_sections([])


class TestTrackImageUpdater:
    def test_update_image(self) -> None:
        plotter = Mock(spec=Plotter)
        background_image = Mock(spec=TrackImage)
        plotter.plot.return_value = background_image
        track_id = TrackId(1)
        track = Mock(spec=Track)
        datastore = Mock(spec=Datastore)
        filter_element_state = Mock(spec=FilterElementState)
        track_view_state = TrackViewState(filter_element_state)
        track_view_state.show_tracks.set(True)
        track.id = track_id
        updater = TrackImageUpdater(datastore, track_view_state, plotter)
        tracks: list[TrackId] = [track_id]

        updater.notify_tracks(tracks)

        assert track_view_state.background_image.get() == background_image

        plotter.plot.assert_called_once()


class TestFilterElementState:
    def test_getters(self) -> None:
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2000, 1, 3)
        classifications = ["car", "truck"]
        filter_element = FilterElement(start_date, end_date, classifications)

        filter_element_state = FilterElementState(filter_element)

        assert filter_element_state.start_date == start_date
        assert filter_element_state.end_date == end_date
        assert filter_element_state.classifications == classifications

    @patch("OTAnalytics.application.state.Subject.notify")
    def test_setters_do_notify(self, mock_notify: Mock) -> None:
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2000, 1, 3)
        classifications = ["car", "truck"]
        filter_element = FilterElement(None, None, [])

        filter_element_state = FilterElementState(filter_element)
        filter_element_state.start_date = start_date
        filter_element_state.end_date = end_date
        filter_element_state.classifications = classifications

        mock_notify.assert_called_with(filter_element)
        assert mock_notify.call_count == 3

        assert filter_element_state.start_date == start_date
        assert filter_element_state.end_date == end_date
        assert filter_element_state.classifications == classifications

    @patch("OTAnalytics.application.state.Subject.register")
    def test_register(self, mock_register: Mock) -> None:
        observer = Mock(spec=Observer)
        filter_element = Mock(spec=FilterElement)

        filter_element_state = FilterElementState(filter_element)
        filter_element_state.register(observer)

        mock_register.assert_called_once_with(observer)
        assert mock_register.call_count == 1
