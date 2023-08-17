from abc import abstractmethod

from OTAnalytics.domain.track import TrackImage


class AbstractFrameCanvas:
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def update_background(self, image: TrackImage) -> None:
        pass

    @abstractmethod
    def clear_image(self) -> None:
        pass
