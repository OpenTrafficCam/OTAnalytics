from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import (
    SectionState,
    TrackImageUpdater,
    TrackObserver,
    TrackPlotter,
    TrackState,
    TrackViewState,
)
from OTAnalytics.domain.section import Section, SectionId, SectionObserver
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


class TestTrackImageUpdater:
    def test_update_image(self) -> None:
        track_id = TrackId(1)
        track = Mock(spec=Track)
        all_tracks = [track]
        all_sections = [Mock(spec=Section)]
        background_image = Mock(spec=TrackImage)
        plotted_tracks = Mock(spec=TrackImage)
        combined_image = Mock(spec=TrackImage)
        datastore = Mock(spec=Datastore)
        track_view_state = TrackViewState()
        track_view_state.show_tracks.set(True)
        track_plotter = Mock(sepc=TrackPlotter)
        track.id = track_id
        datastore.get_all_tracks.return_value = all_tracks
        datastore.get_all_sections.return_value = all_sections
        background_image.width.return_value = 100
        background_image.height.return_value = 100
        background_image.add.return_value = combined_image
        datastore.get_image_of_track.return_value = background_image
        track_plotter.plot.return_value = plotted_tracks
        updater = TrackImageUpdater(datastore, track_view_state, track_plotter)
        tracks: list[TrackId] = [track_id]

        updater.notify_tracks(tracks)

        assert track_view_state.background_image.get() == combined_image
