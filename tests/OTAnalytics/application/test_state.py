from unittest.mock import Mock, call

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

        assert observer.notify.call_args_list == [
            call(first_track),
            call(changed_track),
        ]
