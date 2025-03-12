from abc import ABC

from customtkinter import CTkCanvas

from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas


class AbstractCTkCanvas(AbstractCanvas, CTkCanvas, ABC):
    pass
