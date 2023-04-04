from pathlib import Path
from tkinter.filedialog import askopenfilename
from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkLabel

from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.plugin_ui.constants import PADX, PADY, STICKY


class FrameTracks(CTkFrame):
    def __init__(self, application: OTAnalyticsApplication, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.application = application
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.label = CTkLabel(master=self, text="Tracks")
        self.button_load_tracks = CTkButton(
            master=self,
            text="Load tracks",
            command=self._load_tracks_in_file,
        )

    def _place_widgets(self) -> None:
        self.label.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_load_tracks.grid(
            row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _load_tracks_in_file(self) -> None:
        track_file = askopenfilename(
            title="Load tracks file", filetypes=[("tracks file", "*.ottrk")]
        )
        print(f"Tracks file to load: {track_file}")
        self.application.add_tracks_of_file(track_file=Path(track_file))
