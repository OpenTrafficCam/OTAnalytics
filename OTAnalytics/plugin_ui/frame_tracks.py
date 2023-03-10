from tkinter.filedialog import askopenfilename
from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkLabel

from OTAnalytics.plugin_ui.constants import PADX, PADY, STICKY


class FrameTracks(CTkFrame):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.label = CTkLabel(master=self, text="Tracks")
        self.button_load_tracks = ButtonLoadTracks(
            master=self,
            text="Load tracks",
        )

    def _place_widgets(self) -> None:
        self.label.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_load_tracks.grid(
            row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )


class ButtonLoadTracks(CTkButton):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.bind("<ButtonRelease-1>", self.on_click)

    def on_click(self, events: Any) -> None:
        self.tracks_file = askopenfilename(
            title="Load tracks file", filetypes=[("tracks file", "*.ottrk")]
        )
        print(f"Tracks file to load: {self.tracks_file}")
