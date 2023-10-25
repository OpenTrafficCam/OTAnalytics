from abc import abstractmethod

from OTAnalytics.plugin_ui.customtkinter_gui.abstract_ctk_frame import AbstractCTkFrame


class AbstractFrameTracks(AbstractCTkFrame):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_offset(self, new_offset_x: float, new_offset_y: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def configure_offset_button(self, color: str, enabled: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    def enable_update_offset_button(self, enabled: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_offset_button_color(self, color: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_default_offset_button_color(self) -> str:
        raise NotImplementedError
