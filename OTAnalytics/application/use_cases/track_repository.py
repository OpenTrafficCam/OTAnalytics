from pathlib import Path
from typing import Iterable

from OTAnalytics.application.logger import logger
from OTAnalytics.domain.track import Track, TrackId, TrackIdProvider
from OTAnalytics.domain.track_dataset.track_dataset import TrackDataset
from OTAnalytics.domain.track_repository import (
    RemoveMultipleTracksError,
    TrackFileRepository,
    TrackRepository,
)


class AllTrackIdsProvider(TrackIdProvider):
    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def get_ids(self) -> Iterable[TrackId]:
        return self._track_repository.get_all_ids()


class FilteredTrackIdProviderByTrackIdProvider(TrackIdProvider):
    def __init__(self, other: TrackIdProvider, by: TrackIdProvider):
        self._other = other
        self._by = by

    def get_ids(self) -> set[TrackId]:
        return set(self._other.get_ids()).intersection(self._by.get_ids())


class GetAllTracks:
    """Get all tracks from the track repository.

    Args:
        track_repository (TrackRepository): the track repository to get the tracks from.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def as_list(self) -> list[Track]:
        return self.as_dataset().as_list()

    def as_dataset(self) -> TrackDataset:
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
        return self.as_list()

    def as_list(self) -> list[Track]:
        return self.as_dataset().as_list()

    def as_dataset(self) -> TrackDataset:
        tracks = self._track_repository.get_all()
        return tracks.filter_by_min_detection_length(2)


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

    def __call__(self, tracks: TrackDataset) -> None:
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
        try:
            self._track_repository.remove_multiple(set(track_ids))
        except RemoveMultipleTracksError as cause:
            logger().info(cause)


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


class GetTracksAsBatches:
    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository: TrackRepository = track_repository

    def get(self, batches: int) -> Iterable[TrackDataset]:
        """Get tracks in the repository as batches.

        Args:
            batches (int): the number of batches.

        Returns:
            Iterable[TrackDataset]: the batches of tracks.
        """
        return self._track_repository.split(batches)


class TrackRepositorySize:
    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def get(self) -> int:
        """Get the number of tracks in the repository.

        Returns:
            int: the number of tracks.

        """
        return len(self._track_repository)


class RemoveTracksByOriginalIds:
    """
    Handles the removal of tracks from a repository using their original IDs.

    Args:
        track_repository: The repository instance that provides access to track
            data.
    """

    def __init__(self, track_repository: TrackRepository) -> None:
        self._track_repository = track_repository

    def remove(self, original_ids: frozenset[TrackId]) -> None:
        """
        Removes tracks from the track repository using their original IDs.

        Args:
            original_ids (frozenset[TrackId]): The original track IDs representing
                the tracks to be removed.
        """
        self._track_repository.remove_by_original_ids(original_ids)
