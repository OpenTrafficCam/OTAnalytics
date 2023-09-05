from pathlib import Path
from unittest.mock import Mock

import pytest

from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    ClearAllTracks,
    GetAllTrackFiles,
    GetAllTrackIds,
    GetAllTracks,
)
from OTAnalytics.domain.track import Detection, Track, TrackFileRepository, TrackId, TrackRepository


@pytest.fixture
def tracks() -> list[Mock]:
    return [Mock(spec=Track), Mock(spec=Track)]


@pytest.fixture
def track_files() -> set[Mock]:
    return {Mock(spec=Path), Mock(spec=Path)}


@pytest.fixture
def track_repository(tracks: list[Mock]) -> Mock:
    repository = Mock(spec=TrackRepository)
    repository.get_all.return_value = tracks
    repository.get_all_ids.return_value = {TrackId(1), TrackId(2)}
    return repository


@pytest.fixture
def track_file_repository(track_files: list[Mock]) -> Mock:
    repository = Mock(spec=TrackFileRepository)
    repository.get_all.return_value = track_files
    return repository


class TestGetAllTracks:
    def test_get_all_tracks(self, track_repository: Mock, tracks: list[Mock]) -> None:
        get_all_tracks = GetAllTracks(track_repository)
        result_tracks = get_all_tracks()
        assert result_tracks == tracks
        track_repository.get_all.assert_called_once()


class TestGetAllTrackIds:
    def test_get_all_tracks(self, track_repository: Mock) -> None:
        get_all_track_ids = GetAllTrackIds(track_repository)
        result_tracks = get_all_track_ids()
        assert result_tracks == {TrackId(1), TrackId(2)}
        track_repository.get_all_ids.assert_called_once()


class TestAddAllTracks:
    def test_add_all_tracks(self, track_repository: Mock, tracks: list[Track]) -> None:
        add_all_tracks = AddAllTracks(track_repository)
        add_all_tracks(tracks)
        track_repository.add_all.assert_called_once_with(tracks)


class TestClearAllTracks:
    def test_clear_all_tracks(self, track_repository: Mock) -> None:
        clear_all = ClearAllTracks(track_repository)
        clear_all()
        track_repository.clear.assert_called_once()


class TestGetAllTrackFiles:
    def test_get_all_track_files(
        self, track_file_repository: Mock, track_files: set[Mock]
    ) -> None:
        use_case = GetAllTrackFiles(track_file_repository)
        files = use_case()

        assert track_files == files
        track_file_repository.get_all.assert_called_once()
