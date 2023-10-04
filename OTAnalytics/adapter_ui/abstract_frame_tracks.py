from abc import abstractmethod

from OTAnalytics.plugin_ui.customtkinter_gui.abstract_ctk_frame import AbstractCTkFrame


class AbstractFrameTracks(AbstractCTkFrame):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def update_offset(self, new_offset_x: float, new_offset_y: float) -> None:
        pass
