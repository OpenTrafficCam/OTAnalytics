from abc import abstractmethod

from customtkinter import CTkFrame

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.helpers import WidgetPositionProvider


class AbstractFrameSections(AbstractFrame, WidgetPositionProvider, CTkFrame):
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
