from typing import Any

import customtkinter
from customtkinter import CTk

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.plugin_parser.otvision_parser import OttrkParser
from OTAnalytics.plugin_ui.canvas import FrameCanvas
from OTAnalytics.plugin_ui.constants import PADX, STICKY
from OTAnalytics.plugin_ui.frame_sections import FrameSections
from OTAnalytics.plugin_ui.frame_tracks import FrameTracks


class OTAnalyticsApplication(CTk):
    def __init__(self, title: str = "OTAnalytics", **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.datastore: Datastore

    def _get_widgets(self) -> None:
        self.frame_canvas = FrameCanvas(master=self)
        self.frame_tracks = FrameTracks(master=self)
        self.frame_sections = FrameSections(master=self)

    def _place_widgets(self) -> None:
        PADY = 10
        self.frame_canvas.grid(
            row=0, column=0, rowspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.frame_tracks.grid(row=0, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self.frame_sections.grid(row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY)

    def start(self) -> None:
        self.setup_application()
        self.show_gui()

    def setup_application(self) -> None:
        """
        Build all required objects and inject them where necessary
        """
        track_parser = OttrkParser()
        self.datastore = Datastore(track_parser)

    def show_gui(self) -> None:
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("green")

        # self.geometry("800x600")

        self.title("OTAnalytics")

        self._get_widgets()
        self._place_widgets()

        self.mainloop()
