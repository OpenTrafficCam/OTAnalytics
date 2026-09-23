from pathlib import Path
from unittest.mock import Mock

from OTAnalytics.application.use_cases.deselected_track_files import (
    ClearDeselectedTrackFiles,
    DeselectedTrackFileRepository,
    GetAllConfiguredTrackFiles,
)
from OTAnalytics.application.use_cases.track_repository import GetAllTrackFiles

FIRST_TRACK_FILE = Path("path/to/first.ottrk")
SECOND_TRACK_FILE = Path("path/to/second.ottrk")
THIRD_TRACK_FILE = Path("path/to/third.ottrk")


class TestDeselectedTrackFileRepository:
    def test_add_all_and_get_all(self) -> None:
        repository = DeselectedTrackFileRepository()

        repository.add_all([FIRST_TRACK_FILE])
        repository.add_all([SECOND_TRACK_FILE, FIRST_TRACK_FILE])

        assert repository.get_all() == {FIRST_TRACK_FILE, SECOND_TRACK_FILE}

    def test_get_all_returns_copy(self) -> None:
        repository = DeselectedTrackFileRepository()
        repository.add_all([FIRST_TRACK_FILE])

        repository.get_all().add(SECOND_TRACK_FILE)

        assert repository.get_all() == {FIRST_TRACK_FILE}

    def test_clear(self) -> None:
        repository = DeselectedTrackFileRepository()
        repository.add_all([FIRST_TRACK_FILE])

        repository.clear()

        assert repository.get_all() == set()


class TestClearDeselectedTrackFiles:
    def test_clear(self) -> None:
        repository = DeselectedTrackFileRepository()
        repository.add_all([FIRST_TRACK_FILE])

        ClearDeselectedTrackFiles(repository)()

        assert repository.get_all() == set()


class TestGetAllConfiguredTrackFiles:
    def test_combines_loaded_and_deselected_track_files(self) -> None:
        get_all_track_files = Mock(spec=GetAllTrackFiles)
        get_all_track_files.return_value = {FIRST_TRACK_FILE, SECOND_TRACK_FILE}
        repository = DeselectedTrackFileRepository()
        repository.add_all([SECOND_TRACK_FILE, THIRD_TRACK_FILE])

        target = GetAllConfiguredTrackFiles(get_all_track_files, repository)

        assert target() == {FIRST_TRACK_FILE, SECOND_TRACK_FILE, THIRD_TRACK_FILE}
