from pathlib import Path
from typing import Iterable

from OTAnalytics.domain.track import Track, TrackId, TrackRepository


class GetAllTracks:
    """Get all tracks from the track repository.

    Args:
        track_repository (TrackRepository): the track repository to get the tracks from.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def __call__(self) -> list[Track]:
        return self._track_repository.get_all()


class GetAllTrackIds:
    """Get all track ids from the track repository.

    Args:
        track_repository (TrackRepository): the track repository to get the ids from.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def __call__(self) -> Iterable[TrackId]:
        """Get all track ids from the track repository.

        Returns:
            Iterable[TrackId]: the track ids.
        """
        return self._track_repository.get_all_ids()


class AddAllTracks:
    """Add tracks to the track repository.

    Args:
        track_repository (TrackRepository): the track repository to add the tracks to.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def __call__(self, tracks: Iterable[Track]) -> None:
        self._track_repository.add_all(tracks)


class ClearAllTracks:
    """Clear the track repository.

    Args:
        track_repository (TrackRepository): the track repository to be cleared.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def __call__(self) -> None:
        self._track_repository.clear()


class GetAllTrackFiles:
    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def __call__(self) -> set[Path]:
        return {
            detection.input_file_path
            for track in self._track_repository.get_all()
            for detection in track.detections
        }
