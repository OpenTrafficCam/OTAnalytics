"""Track files that are referenced by a configuration but were not loaded.

Loading only a fraction of the track files of an otconfig must not lose the
remaining ones: they still belong to the configuration and have to be written
back when it is saved. The repository in this module keeps them while the
track repository holds only the files that were actually loaded.
"""

from pathlib import Path
from typing import Iterable

from OTAnalytics.application.use_cases.track_repository import GetAllTrackFiles


class DeselectedTrackFileRepository:
    """Store track files of a configuration that have not been loaded."""

    def __init__(self) -> None:
        self._files: set[Path] = set()

    def add_all(self, files: Iterable[Path]) -> None:
        """Add multiple track files to the repository.

        Args:
            files (Iterable[Path]): the track files to be added.
        """
        self._files.update(files)

    def get_all(self) -> set[Path]:
        """Retrieve all deselected track files.

        Returns:
            set[Path]: a copy of the track files within the repository.
        """
        return set(self._files)

    def clear(self) -> None:
        """Remove all track files from the repository."""
        self._files.clear()


class ClearDeselectedTrackFiles:
    """Clear the deselected track file repository.

    Args:
        deselected_track_file_repository (DeselectedTrackFileRepository): the
            repository to be cleared.
    """

    def __init__(
        self, deselected_track_file_repository: DeselectedTrackFileRepository
    ) -> None:
        self._deselected_track_file_repository = deselected_track_file_repository

    def __call__(self) -> None:
        self._deselected_track_file_repository.clear()


class GetAllConfiguredTrackFiles:
    """Get all track files belonging to the current configuration.

    Combines the track files that have been loaded with those that have been
    deselected while loading a configuration.

    Args:
        get_all_track_files (GetAllTrackFiles): use case to get the loaded track
            files.
        deselected_track_file_repository (DeselectedTrackFileRepository): the
            repository holding the track files that have not been loaded.
    """

    def __init__(
        self,
        get_all_track_files: GetAllTrackFiles,
        deselected_track_file_repository: DeselectedTrackFileRepository,
    ) -> None:
        self._get_all_track_files = get_all_track_files
        self._deselected_track_file_repository = deselected_track_file_repository

    def __call__(self) -> set[Path]:
        return (
            self._get_all_track_files()
            | self._deselected_track_file_repository.get_all()
        )
