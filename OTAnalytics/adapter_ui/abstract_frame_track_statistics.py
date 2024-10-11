from abc import ABC, abstractmethod

from OTAnalytics.application.use_cases.track_statistics import TrackStatistics


class AbstractFrameTrackStatistics(ABC):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_track_statistics(self, track_statistics: TrackStatistics) -> None:
        raise NotImplementedError
