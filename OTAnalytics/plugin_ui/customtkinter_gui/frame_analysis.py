import tkinter
from typing import Any

from customtkinter import CTkButton

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.logging import logger
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.custom_containers import (
    CustomCTkTabview,
    EmbeddedCTkFrame,
)
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import ask_for_save_file_name


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


class FrameAnalysis(EmbeddedCTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
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
        self.button_export_eventlist = CTkButton(
            master=self, text="Export eventlist", command=self._viewmodel.export_events
        )
        self.button_export_counts = CTkButton(
            master=self, text="Export counts", command=self._viewmodel.export_counts
        )

    def _place_widgets(self) -> None:
        # self._label_title.grid(
        #     row=0, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        # )
        self._button_create_events.grid(
            row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._button_save_eventlist.grid(
            row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_export_eventlist.grid(
            row=0, column=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_export_counts.grid(
            row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _create_events(self) -> None:
        logger().info("Creating events")
        self._viewmodel.create_events()

    def _save_eventlist(self) -> None:
        file = ask_for_save_file_name(
            title="Save event list file as",
            filetypes=[("events file", "*.otevents")],
            defaultextension=".otevents",
            initialfile="events.otevents",
        )
        if not file:
            return
        self._viewmodel.save_events(file)
