from pathlib import Path
from unittest.mock import Mock, create_autospec

from OTAnalytics.application.use_cases.deselected_track_files import (
    DeselectedTrackFileRepository,
)
from OTAnalytics.application.use_cases.load_configured_track_files import (
    LoadConfiguredTrackFiles,
)
from OTAnalytics.application.use_cases.select_track_files import (
    SelectEquallySpacedTrackFiles,
)

FIRST_TRACK_FILE = Path("path/to/first.ottrk")
SECOND_TRACK_FILE = Path("path/to/second.ottrk")
THIRD_TRACK_FILE = Path("path/to/third.ottrk")
ALL_TRACK_FILES = {FIRST_TRACK_FILE, SECOND_TRACK_FILE, THIRD_TRACK_FILE}


def create_target(
    load_track_files: Mock, selected_track_files: list[Path]
) -> tuple[LoadConfiguredTrackFiles, DeselectedTrackFileRepository]:
    select_track_files = create_autospec(SelectEquallySpacedTrackFiles, instance=True)
    select_track_files.select.return_value = selected_track_files
    deselected_track_file_repository = DeselectedTrackFileRepository()
    target = LoadConfiguredTrackFiles(
        load_track_files, select_track_files, deselected_track_file_repository
    )
    return target, deselected_track_file_repository


class TestLoadConfiguredTrackFiles:
    def test_loads_selected_track_files(self) -> None:
        load_track_files = Mock()
        target, deselected = create_target(load_track_files, [FIRST_TRACK_FILE])

        target(ALL_TRACK_FILES)

        load_track_files.assert_called_once_with([FIRST_TRACK_FILE])

    def test_remembers_deselected_track_files(self) -> None:
        load_track_files = Mock()
        target, deselected = create_target(load_track_files, [FIRST_TRACK_FILE])

        target(ALL_TRACK_FILES)

        assert deselected.get_all() == {SECOND_TRACK_FILE, THIRD_TRACK_FILE}

    def test_remembers_nothing_if_all_track_files_are_selected(self) -> None:
        load_track_files = Mock()
        target, deselected = create_target(load_track_files, list(ALL_TRACK_FILES))

        target(ALL_TRACK_FILES)

        assert deselected.get_all() == set()
