from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.state import TrackObserver, TrackState
from OTAnalytics.domain.track import TrackId


class TestTrackState:
    def test_notify_observer(self) -> None:
        first_track = TrackId(1)
        changed_track = TrackId(2)
        observer = Mock(spec=TrackObserver)
        state = TrackState()
        state.register(observer)

        state.update(first_track)
        state.update(changed_track)
        state.update(changed_track)

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
