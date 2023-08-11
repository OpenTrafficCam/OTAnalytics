from abc import abstractmethod

from OTAnalytics.plugin_ui.customtkinter_gui.custom_containers import EmbeddedCTkFrame


class AbstractFrameTracks(EmbeddedCTkFrame):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def update_offset(self, new_offset_x: float, new_offset_y: float) -> None:
        pass
