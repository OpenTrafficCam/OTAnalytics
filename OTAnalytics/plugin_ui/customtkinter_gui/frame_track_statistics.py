from typing import Any
from OTAnalytics.plugin_ui.customtkinter_gui.abstract_ctk_frame import AbstractCTkFrame
from OTAnalytics.adapter_ui.view_model import ViewModel
import tkinter
from customtkinter import CTkButton, CTkEntry, CTkLabel, ThemeManager

from OTAnalytics.application.use_cases.track_statistic import TrackStatistics
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.adapter_ui.abstract_frame_track_statistics import AbstractFrameTrackStatistics

class FrameTrackStatistics(AbstractCTkFrame, AbstractFrameTrackStatistics):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._is_initialized = False
        self._viewmodel = viewmodel
        self.default_border_color = ThemeManager.theme["CTkEntry"]["border_color"]
        self._get_widgets()
        self._place_widgets()
        self.introduce_to_viewmodel()
        self._is_initialized = True

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_track_statistics(self)
        
    def _get_widgets(self) -> None:
        self._label = CTkLabel(
            master=self, text="not calculated yet", anchor="nw", justify="right"
        )
        
    def _place_widgets(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._label.grid(
            row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def update_track_statistics(self, track_statistics: TrackStatistics) -> None:
        self._label.configure(text=str(track_statistics))