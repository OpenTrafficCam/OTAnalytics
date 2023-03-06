from unittest.mock import Mock

from OTAnalytics.domain.track import TrackId, TrackRepository


class TestTrackRepository:
    def test_add(self) -> None:
        track = Mock()
        repository = TrackRepository()

        repository.add(track)

        assert track in repository.get_all()

    def test_add_all(self) -> None:
        first_track = Mock()
        second_track = Mock()
        repository = TrackRepository()

        repository.add_all([first_track, second_track])

        assert first_track in repository.get_all()
        assert second_track in repository.get_all()

    def test_get_by_id(self) -> None:
        first_track = Mock()
        first_track.id.return_value = TrackId(1)
        second_track = Mock()
        repository = TrackRepository()
        repository.add_all([first_track, second_track])

        returned = repository.get_for(first_track.id)

        assert returned == first_track
