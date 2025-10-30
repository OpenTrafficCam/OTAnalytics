from abc import ABC, abstractmethod

from OTAnalytics.domain.track_dataset.track_dataset import TrackIdSet


class TrackIdProvider(ABC):
    """Interface to provide track ids."""

    @abstractmethod
    def get_ids(self) -> TrackIdSet:
        """Provide track ids.

        Returns:
            TrackIdSet: the track ids.
        """
        pass
