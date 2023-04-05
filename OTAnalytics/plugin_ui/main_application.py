from typing import Any

import customtkinter
from customtkinter import CTk

from OTAnalytics.adapter_intersect.intersect import (
    ShapelyIntersectImplementationAdapter,
)
from OTAnalytics.application.analysis import RunIntersect
from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import (
    SectionState,
    TrackImageUpdater,
    TrackState,
    TrackViewState,
)
from OTAnalytics.domain.track import CalculateTrackClassificationByMaxConfidence
from OTAnalytics.plugin_intersect.intersect import ShapelyIntersector
from OTAnalytics.plugin_parser.otvision_parser import (
    OtEventListParser,
    OtsectionParser,
    OttrkParser,
    OttrkVideoParser,
)
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    MatplotlibTrackPlotter,
)
from OTAnalytics.plugin_ui.constants import PADX, STICKY
from OTAnalytics.plugin_ui.frame_analysis import FrameAnalysis
from OTAnalytics.plugin_ui.frame_canvas import FrameCanvas
from OTAnalytics.plugin_ui.frame_sections import FrameSections
from OTAnalytics.plugin_ui.frame_tracks import FrameTracks
from OTAnalytics.plugin_video_processing.video_reader import MoviepyVideoReader


class OTAnalyticsCli:
    def __init__(self, application: OTAnalyticsApplication) -> None:
        self._application = application

    def start(self) -> None:
        # TODO parse config and add track and section files
        pass


class OTAnalyticsGui:
    def __init__(self, application: OTAnalyticsApplication, app: CTk = CTk()) -> None:
        self._application = application
        self._app: CTk = app

    def start(self) -> None:
        self._show_gui()

    def _show_gui(self) -> None:
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("green")

        self._app.title("OTAnalytics")

        self._get_widgets()
        self._place_widgets()
        self._wire_widgets()
        self._app.mainloop()

    def _get_widgets(self) -> None:
        self.frame_canvas = FrameCanvas(master=self._app, application=self._application)
        self.frame_tracks = FrameTracks(master=self._app, application=self._application)
        self.frame_sections = FrameSections(
            master=self._app, application=self._application
        )
        self.frame_analysis = FrameAnalysis(
            master=self._app, application=self._application
        )

    def _place_widgets(self) -> None:
        PADY = 10
        self.frame_canvas.grid(
            row=0, column=0, rowspan=3, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.frame_tracks.grid(row=0, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self.frame_sections.grid(row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self.frame_analysis.grid(row=2, column=1, padx=PADX, pady=PADY, sticky=STICKY)

    def _wire_widgets(self) -> None:
        self.frame_canvas.register_at(self._application.track_view_state)


class ApplicationStarter:
    def start_gui(self) -> None:
        application = OTAnalyticsApplication(**self.build_dependencies())
        OTAnalyticsGui(application).start()

    def start_cli(self) -> None:
        datastore = OTAnalyticsApplication(**self.build_dependencies())
        OTAnalyticsCli(datastore).start()

    def build_dependencies(self) -> dict[str, Any]:
        datastore = self._create_datastore()
        return {
            "datastore": datastore,
            "track_state": self._create_track_state(),
            "track_view_state": self._create_track_view_state(datastore),
            "section_state": self._create_section_state(),
            "intersect": self._create_intersect(datastore),
        }

    def _create_datastore(self) -> Datastore:
        """
        Build all required objects and inject them where necessary
        """
        track_parser = OttrkParser(CalculateTrackClassificationByMaxConfidence())
        section_parser = OtsectionParser()
        event_list_parser = OtEventListParser()
        video_parser = OttrkVideoParser(MoviepyVideoReader())
        return Datastore(track_parser, section_parser, event_list_parser, video_parser)

    def _create_track_state(self) -> TrackState:
        return TrackState()

    def _create_track_view_state(self, datastore: Datastore) -> TrackViewState:
        state = TrackViewState()
        track_plotter = MatplotlibTrackPlotter()
        updater = TrackImageUpdater(datastore, state, track_plotter)
        datastore.register_tracks_observer(updater)
        return state

    def _create_section_state(self) -> SectionState:
        return SectionState()

    def _create_intersect(self, datastore: Datastore) -> RunIntersect:
        return RunIntersect(
            datastore._track_repository,
            datastore._section_repository,
            datastore._event_repository,
            intersect_implementation=ShapelyIntersectImplementationAdapter(
                ShapelyIntersector()
            ),
        )
