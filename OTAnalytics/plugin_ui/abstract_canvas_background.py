from abc import abstractmethod

from customtkinter import CTkCanvas

# from OTAnalytics.plugin_ui.canvas_observer import EventHandler


class AbstractCanvasBackground(CTkCanvas):
    # TODO: Properly define abstract property here and in derived class(es)
    # @property
    # @abstractmethod
    # def event_handler(self) -> EventHandler:
    #     pass

    # @abstractmethod
    # def create_line(self, x0: int, y0: int, x1: int, y1: int, tags: str) -> None:
    #     pass

    # @abstractmethod
    # def coords(self, id: str, x0: int, y0: int, x1: int, y1: int) -> None:
    #     pass

    # @abstractmethod
    # def delete(self, id: str) -> None:
    #     pass

    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass
