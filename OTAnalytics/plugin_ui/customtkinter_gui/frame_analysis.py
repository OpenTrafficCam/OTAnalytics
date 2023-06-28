from tkinter.filedialog import asksaveasfilename
from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkLabel

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY


class FrameAnalysis(CTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self._label_title = CTkLabel(master=self, text="Analysis")
        self._button_create_events = CTkButton(
            master=self,
            text="Create events",
            command=self._create_events,
        )
        self._button_save_eventlist = CTkButton(
            master=self,
            text="Save eventlist",
            command=self._save_eventlist,
        )
        self.button_export_counts = CTkButton(
            master=self, text="Export counts", command=self._viewmodel.export_counts
        )

    def _place_widgets(self) -> None:
        self._label_title.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self._button_create_events.grid(
            row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._button_save_eventlist.grid(
            row=2, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_export_counts.grid(
            row=3, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _create_events(self) -> None:
        print("Start analysis")
        self._viewmodel.create_events()

    def _save_eventlist(self) -> None:
        file = asksaveasfilename(
            title="Save event list file as",
            filetypes=[("events file", "*.otevents")],
            defaultextension=".otevents",
        )
        if not file:
            return
        self._viewmodel.save_events(file)
