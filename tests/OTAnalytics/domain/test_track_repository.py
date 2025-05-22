from pathlib import Path
from unittest.mock import MagicMock, Mock, PropertyMock, call

import pytest

from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.domain.track_repository import (
    TrackFileRepository,
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
        track_ids_property = PropertyMock(
            return_value=frozenset([track_1.id, track_2.id])
        )
        tracks = MagicMock(spec=TrackDataset)
        tracks.__len__.return_value = 2
        type(tracks).track_ids = track_ids_property

        merged_dataset = Mock(spec=TrackDataset)
        type(merged_dataset).track_ids = track_ids_property

        dataset = Mock(spec=TrackDataset)
        dataset.add_all.return_value = merged_dataset

        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository(dataset)
        repository.register_tracks_observer(observer)

        repository.add_all(tracks)

        dataset.add_all.assert_called_with(tracks)
        observer.notify_tracks.assert_called_with(
            TrackRepositoryEvent.create_added([track_1.id, track_2.id])
        )

    def test_add_nothing(self) -> None:
        empty_dataset = MagicMock()
        empty_dataset.__len__.return_value = 0

        observer = Mock(spec=TrackListObserver)
        dataset = Mock(spec=TrackDataset)
        repository = TrackRepository(dataset)
        repository.register_tracks_observer(observer)
        repository.add_all(empty_dataset)

        dataset.add_all.assert_not_called()
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
        type(dataset).track_ids = PropertyMock(
            return_value=frozenset([track_1.id, track_2.id])
        )
        dataset.clear.return_value = cleared_dataset
        observer = Mock(spec=TrackListObserver)
        repository = TrackRepository(dataset)
        repository.register_tracks_observer(observer)

        repository.clear()

        assert repository._dataset == cleared_dataset
        assert observer.notify_tracks.call_args_list == [
            call(TrackRepositoryEvent.create_removed([track_1.id, track_2.id]))
        ]

    def test_get_all_ids(self, track_1: Mock, track_2: Mock) -> None:
        ids: frozenset[TrackId] = frozenset()
        dataset = Mock(spec=TrackDataset)
        type(dataset).track_ids = PropertyMock(return_value=ids)
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
            call(TrackRepositoryEvent.create_removed([track_1.id])),
            call(TrackRepositoryEvent.create_removed([track_2.id])),
        ]

    def test_remove_multiple(self, track_1: Track, track_2: Track) -> None:
        tracks_to_remove = frozenset([track_1.id, track_2.id])
        updated_dataset = Mock(spec=TrackDataset)
        type(updated_dataset).track_ids = PropertyMock(return_value=tracks_to_remove)
        dataset = Mock(spec=TrackDataset)
        type(dataset).track_ids = PropertyMock(return_value=tracks_to_remove)
        dataset.remove_multiple.return_value = updated_dataset
        repository = TrackRepository(dataset)

        observer = Mock(spec=TrackListObserver)
        repository.register_tracks_observer(observer)

        repository.remove_multiple({track_1.id, track_2.id})
        dataset.remove_multiple.assert_called_once_with({track_1.id, track_2.id})
        assert observer.notify_tracks.call_args_list == [
            call(TrackRepositoryEvent.create_removed(tracks_to_remove))
        ]

    def test_len(self) -> None:
        expected_size = 3
        dataset = MagicMock(spec=TrackDataset)
        dataset.__len__.return_value = expected_size
        repository = TrackRepository(dataset)

        result = len(repository)

        assert result == expected_size
        dataset.__len__.assert_called_once()

    def test_first_occurrence(self) -> None:
        first_occurrence = Mock()
        dataset = Mock()
        dataset.first_occurrence = first_occurrence
        repository = TrackRepository(dataset)
        assert repository.first_occurrence == first_occurrence

    def test_last_occurrence(self) -> None:
        last_occurrence = Mock()
        dataset = Mock()
        dataset.last_occurrence = last_occurrence
        repository = TrackRepository(dataset)
        assert repository.last_occurrence == last_occurrence

    def test_classifications(self) -> None:
        classifications = Mock()
        dataset = Mock()
        dataset.classifications = classifications
        repository = TrackRepository(dataset)
        assert repository.classifications == classifications

    def test_revert_cuts_for(self) -> None:
        original_id_1 = TrackId("original-1")
        original_id_2 = TrackId("original-2")

        cut_id_1 = TrackId("cut-1")
        cut_id_2 = TrackId("cut-2")
        original_ids = frozenset([original_id_1, original_id_2])
        reverted_ids = frozenset([original_id_1])
        cut_ids = frozenset([cut_id_1, cut_id_2])

        observer = Mock()
        dataset = Mock()
        dataset.revert_cuts_for.return_value = (dataset, reverted_ids, cut_ids)
        target = TrackRepository(dataset)
        target.register_tracks_observer(observer)
        target.revert_cuts_for(original_ids)
        dataset.revert_cuts_for.assert_called_once_with(original_ids)
        observer.notify_tracks.assert_called_once_with(
            TrackRepositoryEvent(added=reverted_ids, removed=cut_ids)
        )

    def test_remove_by_original_ids(self) -> None:
        given_ids_to_remove = frozenset([TrackId("original-1"), TrackId("original-2")])
        given_observer = Mock()
        given_dataset = Mock()
        updated_dataset = Mock()
        removed_ids = frozenset([TrackId("actual-1")])

        given_dataset.remove_by_original_ids.return_value = (
            updated_dataset,
            removed_ids,
        )

        target = TrackRepository(given_dataset)
        target.register_tracks_observer(given_observer)
        target.remove_by_original_ids(given_ids_to_remove)

        assert target._dataset == updated_dataset
        given_observer.notify_tracks.assert_called_once_with(
            TrackRepositoryEvent.create_removed(removed_ids)
        )


class TestTrackFileRepository:
    @pytest.fixture
    def mock_file(self) -> Mock:
        return Mock(spec=Path)

    @pytest.fixture
    def mock_other_file(self) -> Mock:
        return Mock(spec=Path)

    def test_add(self, mock_file: Mock, mock_other_file: Mock) -> None:
        observer = Mock()
        repository = TrackFileRepository()
        repository.register(observer)

        assert repository._files == set()
        repository.add(mock_file)
        assert repository._files == {mock_file}
        repository.add(mock_file)
        assert repository._files == {mock_file}
        repository.add(mock_other_file)
        assert repository._files == {mock_file, mock_other_file}
        assert observer.call_args_list == [
            call([mock_file]),
            call([mock_file]),
            call([mock_other_file]),
        ]

    def test_add_all(self, mock_file: Mock, mock_other_file: Mock) -> None:
        observer = Mock()
        repository = TrackFileRepository()
        repository.register(observer)

        repository.add_all([mock_file, mock_other_file])
        assert repository._files == {mock_file, mock_other_file}
        observer.assert_called_once_with([mock_file, mock_other_file])
