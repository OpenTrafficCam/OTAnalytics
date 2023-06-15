from abc import abstractmethod

from customtkinter import CTkFrame

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame


class AbstractFrameSections(AbstractFrame, CTkFrame):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass
