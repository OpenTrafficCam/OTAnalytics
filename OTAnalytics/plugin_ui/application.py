from abc import abstractmethod
from pathlib import Path

import customtkinter
from customtkinter import CTk

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.domain.track import CalculateTrackClassificationByMaxConfidence
from OTAnalytics.plugin_parser.otvision_parser import (
    OtEventListParser,
    OtsectionParser,
    OttrkParser,
    OttrkVideoParser,
)
from OTAnalytics.plugin_ui.constants import PADX, STICKY
from OTAnalytics.plugin_ui.frame_canvas import FrameCanvas, TrackImage
from OTAnalytics.plugin_ui.frame_sections import FrameSections
from OTAnalytics.plugin_ui.frame_tracks import FrameTracks


class OTAnalyticsApplication:
    def __init__(self, datastore: Datastore) -> None:
        self._datastore: Datastore = datastore

    def add_tracks_of_file(self, track_file: Path) -> None:
        self._datastore.load_track_file(file=track_file)

    def add_sections_of_file(self, sections_file: Path) -> None:
        self._datastore.load_section_file(file=sections_file)

    def start(self) -> None:
        self.start_internal()

    @abstractmethod
    def start_internal(self) -> None:
        pass


class OTAnalyticsCli(OTAnalyticsApplication):
    def __init__(self, datastore: Datastore) -> None:
        super().__init__(datastore)

    def start_internal(self) -> None:
        # TODO parse config and add track and section files
        pass


class OTAnalyticsGui(OTAnalyticsApplication):
    def __init__(self, datastore: Datastore, app: CTk = CTk()) -> None:
        super().__init__(datastore)
        self._app: CTk = app

    def start_internal(self) -> None:
        self._show_gui()

    def _show_gui(self) -> None:
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("green")

        self._app.title("OTAnalytics")

        self._get_widgets()
        self._place_widgets()
        image = TrackImage(
            Path(r"tests/data/Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4")
        )
        self.frame_canvas.add_image(image)
        self._app.mainloop()

    def _get_widgets(self) -> None:
        self.frame_canvas = FrameCanvas(master=self._app)
        self.frame_tracks = FrameTracks(master=self._app, datastore=self._datastore)
        self.frame_sections = FrameSections(master=self._app)

    def _place_widgets(self) -> None:
        PADY = 10
        self.frame_canvas.grid(
            row=0, column=0, rowspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.frame_tracks.grid(row=0, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self.frame_sections.grid(row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY)


class ApplicationStarter:
    def start_gui(self) -> None:
        datastore = self.create_datastore()
        OTAnalyticsGui(datastore).start()

    def start_cli(self) -> None:
        datastore = self.create_datastore()
        OTAnalyticsCli(datastore).start()

    def create_datastore(self) -> Datastore:
        """
        Build all required objects and inject them where necessary
        """
        track_parser = OttrkParser(CalculateTrackClassificationByMaxConfidence())
        section_parser = OtsectionParser()
        event_list_parser = OtEventListParser()
        video_parser = OttrkVideoParser()
        return Datastore(track_parser, section_parser, event_list_parser, video_parser)
