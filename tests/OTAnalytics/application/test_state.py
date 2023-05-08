from datetime import datetime
from typing import Callable, Optional
from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import (
    ObservableOptionalProperty,
    ObservableProperty,
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
        first_filter_element = FilterElement(None, None, [])
        changed_filter_element = FilterElement(
            datetime(2000, 1, 1), datetime(2000, 1, 3), ["car", "truck"]
        )
        observer = Mock(spec=Callable[[FilterElement], None])
        state = ObservableProperty[FilterElement](first_filter_element)
        state.register(observer)

        state.set(changed_filter_element)
        state.set(changed_filter_element)

        assert observer.call_args_list == [
            call(changed_filter_element),
        ]

    def test_update_filter_element_on_on_notify_filter_element(self) -> None:
        filter_element = FilterElement(
            datetime(2000, 1, 1), datetime(2000, 1, 3), ["car", "truck"]
        )
        state = TrackViewState()

        state.filter_element.set(filter_element)

        assert state.filter_element.get() == filter_element


class TestOptionalObservableProperty:
    def test_notify_observer(self) -> None:
        first_section = SectionId("north")
        changed_section = SectionId("south")
        observer = Mock(spec=Callable[[Optional[SectionId]], None])
        state = ObservableOptionalProperty[SectionId]()
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
        track_view_state = TrackViewState()
        track_view_state.show_tracks.set(True)
        track.id = track_id
        updater = TrackImageUpdater(datastore, track_view_state, plotter)
        tracks: list[TrackId] = [track_id]

        updater.notify_tracks(tracks)

        assert track_view_state.background_image.get() == background_image

        plotter.plot.assert_called_once()
