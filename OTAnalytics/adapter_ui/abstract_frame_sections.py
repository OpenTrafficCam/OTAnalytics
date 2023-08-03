from abc import abstractmethod

from customtkinter import CTkFrame

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.helpers import WidgetPositionProvider


class AbstractFrameSections(AbstractFrame, WidgetPositionProvider, CTkFrame):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        raise NotImplementedError
