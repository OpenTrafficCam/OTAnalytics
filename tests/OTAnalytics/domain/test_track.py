from pathlib import Path
from unittest.mock import MagicMock, Mock, call

import pytest

from OTAnalytics.domain.track import (
    Track,
    TrackDataset,
    TrackFileRepository,
    TrackId,
    TrackListObserver,
    TrackObserver,
    TrackRepository,
    TrackRepositoryEvent,
    TrackSubject,
)


class TestTrackSubject:
    def test_notify_observer(self) -> None:
        changed_track = TrackId("1")
        observer = Mock(spec=TrackObserver)
        subject = TrackSubject()
        subject.register(observer)

        subject.notify(changed_track)

        observer.notify_track.assert_called_with(changed_track)


class TestTrackRepository:
    @pytest.fixture
    def track_1(self) -> Mock:
        track = Mock(spec=Track)
        track.id = TrackId("1")
        return track

    @pytest.fixture
    def track_2(self) -> Mock:
        track = Mock(spec=Track)
        track.id = TrackId("2")
        return track

    def test_add_all(self, track_1: Mock, track_2: Mock) -> None:
        tracks = [track_1, track_2]
        merged_dataset = Mock(spec=TrackDataset)
        dataset = Mock(spec=TrackDataset)
        dataset.add_all.return_value = merged_dataset

        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository(dataset)
        repository.register_tracks_observer(observer)

        repository.add_all(tracks)

        dataset.add_all.assert_called_with(tracks)
        observer.notify_tracks.assert_called_with(
            TrackRepositoryEvent([track_1.id, track_2.id], [])
        )

    def test_add_nothing(self) -> None:
        observer = Mock(spec=TrackListObserver)
        dataset = Mock(spec=TrackDataset)
        repository = TrackRepository(dataset)
        repository.register_tracks_observer(observer)
        repository.add_all([])

        dataset.add_all.assert_called_once_with([])
        observer.notify_tracks.assert_not_called()

    def test_get_by_id(self, track_1: Mock) -> None:
        dataset = Mock(spec=TrackDataset)
        dataset.get_for.return_value = track_1
        repository = TrackRepository(dataset)

        returned = repository.get_for(track_1.id)

        assert track_1 == returned
        dataset.get_for.assert_called_with(track_1.id)

    def test_clear(self, track_1: Track, track_2: Track) -> None:
        cleared_dataset = Mock(spec=TrackDataset)
        dataset = Mock(spec=TrackDataset)
        dataset.get_all_ids.return_value = [track_1.id, track_2.id]
        dataset.clear.return_value = cleared_dataset
        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository(dataset)
        repository.register_tracks_observer(observer)

        repository.clear()

        assert repository._dataset == cleared_dataset
        assert observer.notify_tracks.call_args_list == [
            call(TrackRepositoryEvent([], [track_1.id, track_2.id]))
        ]

    def test_get_all_ids(self, track_1: Mock, track_2: Mock) -> None:
        ids: set[TrackId] = set()
        dataset = Mock(spec=TrackDataset)
        dataset.get_all_ids.return_value = ids
        repository = TrackRepository(dataset)

        actual_ids = repository.get_all_ids()

        assert actual_ids is ids

    def test_remove(self, track_1: Track, track_2: Track) -> None:
        dataset = Mock(spec=TrackDataset)
        dataset.remove.return_value = dataset
        repository = TrackRepository(dataset)

        observer = Mock(spec=TrackListObserver)
        repository.register_tracks_observer(observer)

        repository.remove(track_1.id)
        assert len(dataset.remove.call_args_list) == 1
        assert call(track_1.id) in dataset.remove.call_args_list
        repository.remove(track_2.id)
        assert call(track_2.id) in dataset.remove.call_args_list

        assert observer.notify_tracks.call_args_list == [
            call(TrackRepositoryEvent([], [track_1.id])),
            call(TrackRepositoryEvent([], [track_2.id])),
        ]

    def test_remove_multiple(self, track_1: Track, track_2: Track) -> None:
        dataset = Mock(spec=TrackDataset)
        dataset.remove.return_value = dataset
        repository = TrackRepository(dataset)

        observer = Mock(spec=TrackListObserver)
        repository.register_tracks_observer(observer)

        repository.remove_multiple({track_1.id, track_2.id})
        assert len(dataset.remove.call_args_list) == 2
        assert call(track_1.id) in dataset.remove.call_args_list
        assert call(track_2.id) in dataset.remove.call_args_list

    def test_len(self) -> None:
        expected_size = 3
        dataset = MagicMock(spec=TrackDataset)
        dataset.__len__.return_value = expected_size
        repository = TrackRepository(dataset)

        result = len(repository)

        assert result == expected_size
        dataset.__len__.assert_called_once()


class TestTrackFileRepository:
    @pytest.fixture
    def mock_file(self) -> Mock:
        return Mock(spec=Path)

    @pytest.fixture
    def mock_other_file(self) -> Mock:
        return Mock(spec=Path)

    def test_add(self, mock_file: Mock, mock_other_file: Mock) -> None:
        repository = TrackFileRepository()
        assert repository._files == set()
        repository.add(mock_file)
        assert repository._files == {mock_file}
        repository.add(mock_file)
        assert repository._files == {mock_file}
        repository.add(mock_other_file)
        assert repository._files == {mock_file, mock_other_file}

    def test_add_all(self, mock_file: Mock, mock_other_file: Mock) -> None:
        repository = TrackFileRepository()
        repository.add_all([mock_file, mock_other_file])
        assert repository._files == {mock_file, mock_other_file}
