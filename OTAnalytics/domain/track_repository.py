from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from OTAnalytics.application.logger import logger
from OTAnalytics.domain.observer import OBSERVER, Subject
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset.track_dataset import (
    EmptyTrackIdSet,
    TrackDataset,
    TrackIdSet,
)


@dataclass(frozen=True)
class TrackRepositoryEvent:
    added: TrackIdSet
    removed: TrackIdSet

    @staticmethod
    def create_added(tracks: TrackIdSet) -> "TrackRepositoryEvent":
        return TrackRepositoryEvent(tracks, EmptyTrackIdSet())

    @staticmethod
    def create_removed(tracks: TrackIdSet) -> "TrackRepositoryEvent":
        return TrackRepositoryEvent(EmptyTrackIdSet(), tracks)


class TrackListObserver(ABC):
    """
    Interface to listen to changes to a list of tracks.
    """

    @abstractmethod
    def notify_tracks(self, track_event: TrackRepositoryEvent) -> None:
        """
        Notifies that the given tracks have been added.

        Args:
            track_event (TrackRepositoryEvent): list of added or removed tracks.
        """
        raise NotImplementedError


class TrackObserver(ABC):
    """
    Interface to listen to changes of a single track.
    """

    @abstractmethod
    def notify_track(self, track_id: Optional[TrackId]) -> None:
        """
        Notifies that the track of the given id has changed.

        Args:
            track_id (Optional[TrackId]): id of the changed track
        """
        pass


class TrackSubject:
    """
    Helper class to handle and notify observers
    """

    def __init__(self) -> None:
        self.observers: set[TrackObserver] = set()

    def register(self, observer: TrackObserver) -> None:
        """
        Listen to events.

        Args:
            observer (TrackObserver): listener to add
        """
        self.observers.add(observer)

    def notify(self, track_id: Optional[TrackId]) -> None:
        """
        Notifies observers about the track id.

        Args:
            track_id (Optional[TrackId]): id of the changed track
        """
        [observer.notify_track(track_id) for observer in self.observers]


class TrackRemoveError(Exception):
    def __init__(self, track_id: TrackId, message: str) -> None:
        """Exception to be raised if track can not be removed.

        Args:
            track_id (TrackId): the track id of the track to be removed.
            message (str): the error message.
        """
        super().__init__(message)
        self._track_id = track_id


class RemoveMultipleTracksError(Exception):
    """Exception to be raised if multiple tracks can not be removed.

    Args:
        track_ids (list[TrackId]): the track id of the track to be removed.
        message (str): the error message.
    """

    def __init__(self, track_ids: list[TrackId], message: str):
        super().__init__(message)
        self._track_ids = track_ids


class TrackRepository:
    @property
    def first_occurrence(self) -> datetime | None:
        return self._dataset.first_occurrence

    @property
    def last_occurrence(self) -> datetime | None:
        return self._dataset.last_occurrence

    @property
    def classifications(self) -> frozenset[str]:
        return self._dataset.classifications

    def __init__(self, dataset: TrackDataset) -> None:
        self._dataset = dataset
        self.observers = Subject[TrackRepositoryEvent]()

    def register_tracks_observer(self, observer: TrackListObserver) -> None:
        """
        Listen to changes of the repository.

        Args:
            observer (TrackListObserver): listener to be notified about changes
        """
        self.observers.register(observer.notify_tracks)

    def add_all(self, tracks: TrackDataset) -> None:
        """
        Add multiple tracks to the repository and notify only once about it.

        Args:
            tracks (TrackDataset): tracks to be added.
        """
        if len(tracks):
            self._dataset = self._dataset.add_all(tracks)
            self.observers.notify(TrackRepositoryEvent.create_added(tracks.track_ids))

    def get_for(self, id: TrackId) -> Optional[Track]:
        """
        Retrieve a track for the given id.

        Args:
            id (TrackId): id to search for

        Returns:
            Optional[Track]: track if it exists
        """
        return self._dataset.get_for(id)

    def get_all(self) -> TrackDataset:
        """
        Retrieve all tracks.

        Returns:
            list[Track]: all tracks within the repository
        """
        return self._dataset

    def get_all_ids(self) -> TrackIdSet:
        """Get all track ids in this repository.

        Returns:
            Iterable[TrackId]: the track ids.
        """
        return self._dataset.track_ids

    def remove_multiple(self, track_ids: TrackIdSet) -> None:
        not_existing_tracks = track_ids.difference(self._dataset.track_ids)
        if not_existing_tracks:
            logger().warning(
                f"Trying to remove {len(not_existing_tracks)} "
                "track(s) not contained in track dataset."
            )
            logger().debug(
                "Trying to remove tracks not contained in dataset: "
                f"{not_existing_tracks}."
            )
        self._dataset = self._dataset.remove_multiple(track_ids)
        self.observers.notify(TrackRepositoryEvent.create_removed(track_ids))

    def split(self, chunks: int) -> Iterable[TrackDataset]:
        return self._dataset.split(chunks)

    def clear(self) -> None:
        """
        Clear the repository and inform the observers about the empty repository.
        """
        removed = self._dataset.track_ids
        self._dataset = self._dataset.clear()
        self.observers.notify(TrackRepositoryEvent.create_removed(removed))

    def __len__(self) -> int:
        return len(self._dataset)

    def revert_cuts_for(self, original_ids: TrackIdSet) -> None:
        """
        Reverts cuts for tracks associated with the provided original track IDs.

        This method finds any cut tracks derived from the original track IDs and
        restores them to their original state. It replaces cut track IDs with their
        original track IDs in the dataset, removing the cut versions.

        The method operates on the current dataset without modification if either:
        - The dataset is empty
        - None of the provided original track IDs have associated cut tracks

        Observers registered with the repository will be notified of both removed tracks
        (the cut versions) and new/updated tracks (the reverted original tracks).

        Args:
            original_ids (TrackIdSet): track IDs representing the
                original tracks for which cuts should be reverted.
        """

        reverted_dataset, reverted_ids, cut_track_ids = self._dataset.revert_cuts_for(
            original_ids
        )
        self._dataset = reverted_dataset
        self.observers.notify(
            TrackRepositoryEvent(added=reverted_ids, removed=cut_track_ids)
        )

    def remove_by_original_ids(self, original_ids: TrackIdSet) -> None:
        """
        Removes tracks from the repository based on their original IDs and notifies
        observers of the removal event.

        Args:
            original_ids (TrackIdSet): original IDs of the tracks to be removed.
        """
        updated_dataset, removed_ids = self._dataset.remove_by_original_ids(
            original_ids
        )
        self._dataset = updated_dataset
        self.observers.notify(TrackRepositoryEvent.create_removed(removed_ids))


@dataclass(frozen=True)
class TrackFileRepositoryEvent:
    added: list[Path]
    removed: list[Path]

    @staticmethod
    def create_added(files: Iterable[Path]) -> "TrackFileRepositoryEvent":
        return TrackFileRepositoryEvent(list(files), [])

    @staticmethod
    def create_removed(files: Iterable[Path]) -> "TrackFileRepositoryEvent":
        return TrackFileRepositoryEvent([], list(files))


class TrackFileRepository:
    def __init__(self) -> None:
        self._files: set[Path] = set()
        self._subject = Subject[TrackFileRepositoryEvent]()

    def add(self, file: Path) -> None:
        """
        Add a single track file the repository.

        Args:
            file (Path): track file to be added.
        """
        self.__add(file)
        self._subject.notify(TrackFileRepositoryEvent.create_added([file]))

    def __add(self, file: Path) -> None:
        """Add a single track file the repository without notifying observers.

        Args:
            file (Path): track file to be added.
        """
        self._files.add(file)

    def add_all(self, files: Iterable[Path]) -> None:
        """
        Add multiple files to the repository.

        Args:
            files (Iterable[Path]): the files to be added.
        """
        for file in files:
            self.__add(file)
        self._subject.notify(TrackFileRepositoryEvent.create_added(files))

    def get_all(self) -> set[Path]:
        """
        Retrieve all track files.

        Returns:
            set[Path]: all tracks within the repository.
        """
        return self._files.copy()

    def register(self, observer: OBSERVER[Iterable[Path]]) -> None:
        self._subject.register(observer)

    def clear(self) -> None:
        removed_files = self._files.copy()
        self._files.clear()
        self._subject.notify(TrackFileRepositoryEvent.create_removed(removed_files))
