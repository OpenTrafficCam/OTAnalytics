from abc import ABC, abstractmethod


class AbstractFrameTrackPlotting(ABC):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def reset_layers(self) -> None:
        raise NotImplementedError
