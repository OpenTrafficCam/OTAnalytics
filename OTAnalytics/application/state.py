from abc import ABC, abstractmethod
from typing import Optional

from OTAnalytics.domain.track import TrackId


class TrackObserver(ABC):
    @abstractmethod
    def notify(self, track_id: Optional[TrackId]) -> None:
        pass


class TrackState:
    def __init__(self) -> None:
        self.selected_track: Optional[TrackId] = None
        self.observers: list[TrackObserver] = []

    def register(self, observer: TrackObserver) -> None:
        self.observers.append(observer)

    def update(self, track_id: TrackId) -> None:
        if self.selected_track != track_id:
            self.selected_track = track_id
            self._notify_observers()

    def _notify_observers(self) -> None:
        [observer.notify(self.selected_track) for observer in self.observers]
