from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkLabel
from plugin_ui.view_model import ViewModel

from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.plugin_ui.constants import PADX, PADY, STICKY


class FrameTracks(CTkFrame):
    def __init__(
        self, application: OTAnalyticsApplication, viewmodel: ViewModel, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.application = application
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.label = CTkLabel(master=self, text="Tracks")
        self.button_load_tracks = CTkButton(
            master=self, text="Load tracks", command=self._viewmodel.load_tracks
        )

    def _place_widgets(self) -> None:
        self.label.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_load_tracks.grid(
            row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
