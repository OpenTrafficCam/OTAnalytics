from abc import abstractmethod

from customtkinter import CTkFrame

from OTAnalytics.domain.track import TrackImage


class AbstractTracksCanvas(CTkFrame):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def update_show_tracks(self, value: bool) -> None:
        pass

    @abstractmethod
    def update_background(self, image: TrackImage) -> None:
        pass
