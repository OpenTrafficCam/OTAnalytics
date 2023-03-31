from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkLabel

from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.plugin_ui.constants import PADX, PADY, STICKY


class FrameAnalysis(CTkFrame):
    def __init__(self, application: OTAnalyticsApplication, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.application = application
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.label = CTkLabel(master=self, text="Analysis")
        self.button_load_tracks = CTkButton(
            master=self,
            text="Start analysis",
            command=self._start_analysis,
        )

    def _place_widgets(self) -> None:
        self.label.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_load_tracks.grid(
            row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _start_analysis(self) -> None:
        print("Start analysis")
        self.application.start_analysis()
