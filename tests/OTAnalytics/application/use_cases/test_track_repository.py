from pathlib import Path
from typing import Iterable
from unittest.mock import MagicMock, Mock, patch

import pytest

from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    ClearAllTracks,
    FilteredTrackIdProviderByTrackIdProvider,
    GetAllTrackFiles,
    GetAllTrackIds,
    GetAllTracks,
    GetTracksAsBatches,
    GetTracksFromIds,
    GetTracksWithoutSingleDetections,
    RemoveTracks,
    RemoveTracksByOriginalIds,
    TrackRepositorySize,
)
from OTAnalytics.domain.track import Track, TrackId, TrackIdProvider
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.domain.track_repository import TrackFileRepository, TrackRepository


@pytest.fixture
def tracks() -> TrackDataset:
    tracks = [Mock(spec=Track), Mock(spec=Track)]
    dataset = MagicMock(spec=TrackDataset)
    dataset.__iter__.return_value = tracks
    return dataset


@pytest.fixture
def track_files() -> set[Mock]:
    return {Mock(spec=Path), Mock(spec=Path)}


@pytest.fixture
def track_repository(tracks: list[Mock]) -> Mock:
    repository = Mock(spec=TrackRepository)
    repository.get_all.return_value = tracks
    repository.get_all_ids.return_value = {TrackId("1"), TrackId("2")}
    return repository


@pytest.fixture
def track_file_repository(track_files: list[Mock]) -> Mock:
    repository = Mock(spec=TrackFileRepository)
    repository.get_all.return_value = track_files
    return repository


def create_track_ids_from_ids(ids: Iterable[str]) -> Iterable[TrackId]:
    return [TrackId(id) for id in ids]


@pytest.fixture
def track_id_provider() -> Mock:
    return Mock(spec=TrackIdProvider)


class TestFilteredTrackIdProviderByTrackIdProvider:
    """
    https://openproject.platomo.de/wp/5990
    """

    def test_get_ids_of_filter_by_self(self, track_id_provider: Mock) -> None:
        track_ids = create_track_ids_from_ids(["0", "8", "15"])
        track_id_provider.get_ids.return_value = track_ids

        filtered_provider = FilteredTrackIdProviderByTrackIdProvider(
            track_id_provider, track_id_provider
        )
        filtered_ids = filtered_provider.get_ids()

        assert filtered_ids == set(track_ids)
        assert track_id_provider.get_ids.call_count == 2

    def test_get_ids(self, track_id_provider: Mock) -> None:
        track_id_provider.get_ids.return_value = create_track_ids_from_ids(
            ["1", "2", "3"]
        )
        filter = Mock(spec=TrackIdProvider)
        filter.get_ids.return_value = create_track_ids_from_ids(["2", "3", "4"])

        filtered_provider = FilteredTrackIdProviderByTrackIdProvider(
            track_id_provider, filter
        )
        filtered_ids = filtered_provider.get_ids()

        assert filtered_ids == set(create_track_ids_from_ids(["2", "3"]))
        track_id_provider.get_ids.assert_called_once()
        filter.get_ids.assert_called_once()


class TestGetAllTracks:
    def test_get_as_dataset(self) -> None:
        expected_dataset = Mock()
        track_repository = Mock()
        track_repository.get_all.return_value = expected_dataset

        get_tracks = GetAllTracks(track_repository)
        result_dataset = get_tracks.as_dataset()
        assert result_dataset == expected_dataset
        track_repository.get_all.assert_called_once()

    def test_get_as_list(self) -> None:
        first_track = Mock()
        second_track = Mock()
        track_dataset = Mock()
        track_dataset.as_list.return_value = [first_track, second_track]
        track_repository = Mock()
        track_repository.get_all.return_value = track_dataset

        get_tracks = GetAllTracks(track_repository)
        all_tracks = get_tracks.as_list()
        assert all_tracks == [first_track, second_track]
        track_repository.get_all.assert_called_once()
        track_dataset.as_list.assert_called_once()


class TestGetAllTrackIds:
    def test_get_all_tracks(self, track_repository: Mock) -> None:
        get_all_track_ids = GetAllTrackIds(track_repository)
        result_tracks = get_all_track_ids()
        assert result_tracks == {TrackId("1"), TrackId("2")}
        track_repository.get_all_ids.assert_called_once()


class TestAddAllTracks:
    def test_add_all_tracks(self, track_repository: Mock, tracks: TrackDataset) -> None:
        add_all_tracks = AddAllTracks(track_repository)
        add_all_tracks(tracks)
        track_repository.add_all.assert_called_once_with(tracks)


class TestClearAllTracks:
    def test_clear_all_tracks(self, track_repository: Mock) -> None:
        clear_all = ClearAllTracks(track_repository)
        clear_all()
        track_repository.clear.assert_called_once()


class TestRemoveTracks:
    def test_remove(self, track_repository: Mock) -> None:
        remove_ids = [TrackId("1"), TrackId("2")]
        remove_tracks = RemoveTracks(track_repository)
        remove_tracks(remove_ids)
        track_repository.remove_multiple.assert_called_once_with(set(remove_ids))


class TestGetTracksFromIds:
    def test_get_ids(self, track_repository: Mock) -> None:
        track_1 = Mock()
        track_1.id = TrackId("1")
        track_repository.get_for.return_value = track_1

        get_tracks_from_ids = GetTracksFromIds(track_repository)
        tracks = get_tracks_from_ids([track_1.id])
        assert tracks == [track_1]
        track_repository.get_for.assert_called_once_with(track_1.id)


class TestGetTracksWithoutSingleDetections:
    def test_get_as_dataset(self) -> None:
        expected_dataset = Mock()
        dataset = Mock()
        dataset.filter_by_min_detection_length.return_value = expected_dataset
        track_repository = Mock()
        track_repository.get_all.return_value = dataset

        get_tracks = GetTracksWithoutSingleDetections(track_repository)
        result_dataset = get_tracks.as_dataset()
        assert result_dataset == expected_dataset
        track_repository.get_all.assert_called_once()
        dataset.filter_by_min_detection_length.assert_called_once_with(2)

    def test_get_as_list(self) -> None:
        track_repository = Mock()

        get_tracks = GetTracksWithoutSingleDetections(track_repository)
        with patch.object(
            GetTracksWithoutSingleDetections, "as_dataset"
        ) as mock_as_dataset:
            expected_list = Mock()
            filtered_dataset = Mock()
            filtered_dataset.as_list.return_value = expected_list

            mock_as_dataset.return_value = filtered_dataset
            result = get_tracks.as_list()

            assert result == expected_list
            mock_as_dataset.assert_called_once()
            filtered_dataset.as_list.assert_called_once()


class TestGetTracksAsBatches:
    def test_get(self, track_repository: Mock) -> None:
        expected_batches = [Mock(), Mock()]
        track_repository.split.return_value = expected_batches

        get_track_batches = GetTracksAsBatches(track_repository)
        result = get_track_batches.get(batches=4)

        assert result == expected_batches
        track_repository.split.assert_called_once_with(4)


class TestGetAllTrackFiles:
    def test_get_all_track_files(
        self, track_file_repository: Mock, track_files: set[Mock]
    ) -> None:
        use_case = GetAllTrackFiles(track_file_repository)
        files = use_case()

        assert track_files == files
        track_file_repository.get_all.assert_called_once()


class TestTrackRepositorySize:
    def test_get(self) -> None:
        expected_size = 3
        track_repository = MagicMock()
        track_repository.__len__.return_value = expected_size

        track_repository_size = TrackRepositorySize(track_repository)
        result = track_repository_size.get()
        assert result == expected_size
        track_repository.__len__.assert_called_once()


class TestRemoveTracksByOriginalIds:
    def test_remove(self) -> None:
        given_track_repository = Mock()
        given_original_ids = frozenset([TrackId("1"), TrackId("2")])

        target = RemoveTracksByOriginalIds(given_track_repository)
        target.remove(given_original_ids)

        given_track_repository.remove_by_original_ids.assert_called_once_with(
            given_original_ids
        )
