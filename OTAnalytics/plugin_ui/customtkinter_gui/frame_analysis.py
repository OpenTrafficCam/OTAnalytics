import tkinter
from typing import Any

from customtkinter import CTkButton

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.abstract_ctk_frame import AbstractCTkFrame
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.custom_containers import CustomCTkTabview


class TabviewAnalysis(CustomCTkTabview):
    def __init__(
        self,
        viewmodel: ViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._title: str = "Analysis"
        self._get_widgets()
        self._place_widgets()
        self.disable_segmented_button()

    def _get_widgets(self) -> None:
        self.add(self._title)
        self.frame_analysis = FrameAnalysis(
            master=self.tab(self._title), viewmodel=self._viewmodel
        )

    def _place_widgets(self) -> None:
        self.frame_analysis.pack(fill=tkinter.BOTH, expand=True)
        self.set(self._title)


class FrameAnalysis(AbstractCTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_analysis_frame(self)

    def _get_widgets(self) -> None:
        self.button_export_eventlist = CTkButton(
            master=self,
            text="Export eventlist ...",
            command=self._viewmodel.export_events,
        )
        self.button_export_counts = CTkButton(
            master=self, text="Export counts ...", command=self._viewmodel.export_counts
        )

    def _place_widgets(self) -> None:
        self.button_export_eventlist.grid(
            row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_export_counts.grid(
            row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def get_general_buttons(self) -> list[CTkButton]:
        return [self.button_export_counts, self.button_export_eventlist]
