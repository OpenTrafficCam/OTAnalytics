from abc import ABC, abstractmethod

from OTAnalytics.plugin_ui.abstract_canvas_background import AbstractCanvasBackground


class ViewModel(ABC):
    @abstractmethod
    def set_canvas(self, canvas: AbstractCanvasBackground) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_treeview_sections(self, canvas: AbstractCanvasBackground) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_sections(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_sections(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_section(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_section(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def edit_section_geometry(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def edit_section_metadata(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_new_section_geometry(
        self, point0: tuple[int, int], point1: tuple[int, int]
    ) -> None:
        raise NotImplementedError
