from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from OTAnalytics.domain.observer import Subject
from OTAnalytics.domain.track import Track, TrackId
from OTAnalytics.domain.track_dataset import TrackDataset


@dataclass(frozen=True)
class TrackRepositoryEvent:
    added: list[TrackId]
    removed: list[TrackId]


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
            new_tracks = list(tracks.track_ids)
            self.observers.notify(TrackRepositoryEvent(new_tracks, []))

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

    def get_all_ids(self) -> Iterable[TrackId]:
        """Get all track ids in this repository.

        Returns:
            Iterable[TrackId]: the track ids.
        """
        return self._dataset.track_ids

    def remove(self, track_id: TrackId) -> None:
        """Remove track by its id and notify observers

        Raises:
            TrackRemoveError: if track does not exist in repository.

        Args:
            track_id (TrackId): the id of the track to be removed.
        """
        try:
            self._dataset = self._dataset.remove(track_id)
        except KeyError:
            raise TrackRemoveError(
                track_id, f"Trying to remove non existing track with id '{track_id.id}'"
            )
        # TODO: Pass removed track id to notify when moving observers to
        #  application layer
        self.observers.notify(TrackRepositoryEvent([], [track_id]))

    def remove_multiple(self, track_ids: set[TrackId]) -> None:
        failed_tracks: list[TrackId] = []
        for track_id in track_ids:
            try:
                self._dataset = self._dataset.remove(track_id)
            except KeyError:
                failed_tracks.append(track_id)
            # TODO: Pass removed track id to notify when moving observers to
            #  application layer

        if failed_tracks:
            raise RemoveMultipleTracksError(
                failed_tracks,
                (
                    "Multiple tracks with following ids could not be removed."
                    f" '{[failed_track.id for failed_track in failed_tracks]}'"
                ),
            )
        self.observers.notify(TrackRepositoryEvent([], list(track_ids)))

    def split(self, chunks: int) -> Iterable[TrackDataset]:
        return self._dataset.split(chunks)

    def clear(self) -> None:
        """
        Clear the repository and inform the observers about the empty repository.
        """
        removed = list(self._dataset.track_ids)
        self._dataset = self._dataset.clear()
        self.observers.notify(TrackRepositoryEvent([], removed))

    def __len__(self) -> int:
        return len(self._dataset)


class TrackFileRepository:
    def __init__(self) -> None:
        self._files: set[Path] = set()

    def add(self, file: Path) -> None:
        """
        Add a single track file the repository.

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
            self.add(file)

    def get_all(self) -> set[Path]:
        """
        Retrieve all track files.

        Returns:
            set[Path]: all tracks within the repository.
        """
        return self._files.copy()
