from pathlib import Path
from typing import Iterable

from OTAnalytics.domain.track import (
    Track,
    TrackFileRepository,
    TrackId,
    TrackRemoveError,
    TrackRepository,
)


class GetAllTracks:
    """Get all tracks from the track repository.

    Args:
        track_repository (TrackRepository): the track repository to get the tracks from.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def __call__(self) -> list[Track]:
        return self._track_repository.get_all()


class GetTracksWithoutSingleDetections:
    """Get tracks that have at least two detections.

    Returns:
        list[Track]: tracks with at least two detections.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def __call__(self) -> list[Track]:
        """Get tracks that have at least two detections.

        Returns:
            list[Track]: tracks with at least two detections.
        """
        tracks = self._track_repository.get_all()
        return [track for track in tracks if len(track.detections) > 1]


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
    def __init__(self, track_file_repository: TrackFileRepository) -> None:
        self._track_file_repository = track_file_repository

    def __call__(self) -> set[Path]:
        return self._track_file_repository.get_all()


class RemoveTracks:
    """Use case to remove tracks from track repository.

    Tracks that do not exist in the repository will be skipped.

    Args:
        track_repository (TrackRepository): the repository to remove the tracks from.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def __call__(self, track_ids: Iterable[TrackId]) -> None:
        """Remove tracks from track repository.

        Tracks that do not exist in the repository will be skipped.

        Args:
            track_ids (Iterable[TrackId]): ids of tracks to be removed.
        """
        for track_id in track_ids:
            try:
                self._track_repository.remove(track_id)
            except TrackRemoveError:
                continue


class GetTracksFromIds:
    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def __call__(self, track_ids: Iterable[TrackId]) -> Iterable[Track]:
        """Get tracks from ids.

        Non-existing ids will be omitted.

        Args:
            track_ids (Iterable[TrackId]): the ids of the tracks to get.

        Returns:
            Iterable[Track]: the tracks with the ids to get.
        """
        tracks: list[Track] = []
        for track_id in track_ids:
            if track := self._track_repository.get_for(track_id):
                tracks.append(track)

        return tracks
