from pathlib import Path
from tkinter.filedialog import askopenfilename
from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkLabel

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.plugin_ui.constants import PADX, PADY, STICKY


class FrameTracks(CTkFrame):
    def __init__(self, datastore: Datastore, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._datastore = datastore
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
        self._datastore.load_track_file(file=Path(track_file))
