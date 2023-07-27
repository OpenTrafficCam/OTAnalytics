from abc import abstractmethod

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.helpers import WidgetPositionProvider
from OTAnalytics.plugin_ui.customtkinter_gui.custom_containers import EmbeddedCTkFrame


class AbstractFrameSections(AbstractFrame, WidgetPositionProvider, EmbeddedCTkFrame):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def enable_edit_geometry_button(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def disable_edit_geometry_button(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def enable_edit_metadata_button(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def disable_edit_metadata_button(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def enable_remove_button(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def disable_remove_button(self) -> None:
        raise NotImplementedError
