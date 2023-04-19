from pathlib import Path
from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkLabel

from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY


class FrameAnalysis(CTkFrame):
    def __init__(self, application: OTAnalyticsApplication, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._application = application
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.label = CTkLabel(master=self, text="Analysis")
        self.button_load_tracks = CTkButton(
            master=self,
            text="Start analysis",
            command=self._start_analysis,
        )
        self.button_save_eventlist = CTkButton(
            master=self,
            text="Save Eventlist",
            command=self._save_eventlist,
        )

    def _place_widgets(self) -> None:
        self.label.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_load_tracks.grid(
            row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_save_eventlist.grid(
            row=2, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _start_analysis(self) -> None:
        print("Start analysis")
        self._application.start_analysis()

    def _save_eventlist(self) -> None:
        file = Path("./events.json.bz2")
        # asksaveasfilename(
        #     title="Load sections file",
        #     filetypes=[("events file", "*.json.bz2")],
        #     initialdir=Path("."),
        # )
        print(f"Eventlist file to save: {file}")
        self._application.save_events(file=Path(file))
