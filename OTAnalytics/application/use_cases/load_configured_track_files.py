"""Load the track files of a configuration.

Only a portion of the track files of a configuration may be loaded. The
remaining ones still belong to the configuration and are remembered so that
they are not lost when the configuration is saved again.
"""

from pathlib import Path

from OTAnalytics.application.use_cases.deselected_track_files import (
    DeselectedTrackFileRepository,
)
from OTAnalytics.application.use_cases.load_track_files import LoadTrackFiles
from OTAnalytics.application.use_cases.select_track_files import (
    SelectEquallySpacedTrackFiles,
)


class LoadConfiguredTrackFiles:
    """Load the selected track files of a configuration.

    Args:
        load_track_files (LoadTrackFiles): use case to load track files.
        select_track_files (SelectEquallySpacedTrackFiles): selects the portion
            of the track files to be loaded.
        deselected_track_file_repository (DeselectedTrackFileRepository): the
            repository to remember the track files that are not loaded.
    """

    def __init__(
        self,
        load_track_files: LoadTrackFiles,
        select_track_files: SelectEquallySpacedTrackFiles,
        deselected_track_file_repository: DeselectedTrackFileRepository,
    ) -> None:
        self._load_track_files = load_track_files
        self._select_track_files = select_track_files
        self._deselected_track_file_repository = deselected_track_file_repository

    def __call__(self, track_files: set[Path]) -> None:
        """Load the selected track files and remember the remaining ones.

        Args:
            track_files (set[Path]): all track files of the configuration.
        """
        track_files_to_load = self._select_track_files.select(track_files)
        self._load_track_files(track_files_to_load)
        self._deselected_track_file_repository.add_all(
            track_files - set(track_files_to_load)
        )
