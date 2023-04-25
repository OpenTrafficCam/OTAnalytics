import customtkinter
from customtkinter import CTk

from OTAnalytics.adapter_intersect.intersect import (
    ShapelyIntersectImplementationAdapter,
)
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.analysis import RunIntersect, RunSceneEventDetection
from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.datastore import (
    Datastore,
    EventListParser,
    SectionParser,
    TrackParser,
)
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.state import (
    SectionState,
    TrackImageUpdater,
    TrackState,
    TrackViewState,
)
from OTAnalytics.domain.event import SceneEventBuilder
from OTAnalytics.domain.track import (
    CalculateTrackClassificationByMaxConfidence,
    TrackRepository,
)
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
from OTAnalytics.plugin_ui.cli import (
    CliArgumentParser,
    CliArguments,
    CliParseError,
    OTAnalyticsCli,
)
from OTAnalytics.plugin_ui.constants import PADX, STICKY
from OTAnalytics.plugin_ui.dummy_viewmodel import DummyViewModel
from OTAnalytics.plugin_ui.frame_analysis import FrameAnalysis
from OTAnalytics.plugin_ui.frame_canvas import TracksCanvas
from OTAnalytics.plugin_ui.frame_sections import FrameSections
from OTAnalytics.plugin_ui.frame_tracks import TracksFrame
from OTAnalytics.plugin_video_processing.video_reader import MoviepyVideoReader


class OTAnalyticsGui:
    def __init__(
        self,
        view_model: ViewModel,
        app: CTk = CTk(),
    ) -> None:
        self._view_model = view_model
        self._app: CTk = app

    def start(self) -> None:
        self._show_gui()

    def _show_gui(self) -> None:
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("green")

        self._app.title("OTAnalytics")

        self._get_widgets()
        self._place_widgets()
        self._app.mainloop()

    def _get_widgets(self) -> None:
        self.frame_canvas = TracksCanvas(
            master=self._app,
            viewmodel=self._view_model,
        )
        self.frame_tracks = TracksFrame(
            master=self._app,
            viewmodel=self._view_model,
        )
        self.frame_sections = FrameSections(
            master=self._app,
            viewmodel=self._view_model,
        )
        self.frame_analysis = FrameAnalysis(
            master=self._app, viewmodel=self._view_model
        )

    def _place_widgets(self) -> None:
        PADY = 10
        self.frame_canvas.grid(
            row=0, column=0, rowspan=3, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.frame_tracks.grid(row=0, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self.frame_sections.grid(row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self.frame_analysis.grid(row=2, column=1, padx=PADX, pady=PADY, sticky=STICKY)


class ApplicationStarter:
    def start(self) -> None:
        parser = self._build_cli_argument_parser()
        cli_args = parser.parse()

        if cli_args.start_cli:
            try:
                self.start_cli(cli_args)
            except CliParseError as e:
                print(e)
        else:
            self.start_gui()

    def _build_cli_argument_parser(self) -> CliArgumentParser:
        return CliArgumentParser()

    def start_gui(self) -> None:
        datastore = self._create_datastore()
        track_state = self._create_track_state()
        track_view_state = self._create_track_view_state(datastore)
        section_state = self._create_section_state()
        intersect = self._create_intersect()
        scene_event_detection = self._create_scene_event_detection()
        application = OTAnalyticsApplication(
            datastore=datastore,
            track_state=track_state,
            track_view_state=track_view_state,
            section_state=section_state,
            intersect=intersect,
            scene_event_detection=scene_event_detection,
        )
        section_parser: SectionParser = application._datastore._section_parser
        dummy_viewmodel = DummyViewModel(application, section_parser)
        application.connect_observers()
        OTAnalyticsGui(dummy_viewmodel).start()

    def start_cli(self, cli_args: CliArguments) -> None:
        track_parser = self._create_track_parser(self._create_track_repository())
        section_parser = self._create_section_parser()
        event_list_parser = self._create_event_list_parser()
        intersect = self._create_intersect()
        scene_event_detection = self._create_scene_event_detection()
        OTAnalyticsCli(
            cli_args,
            track_parser=track_parser,
            section_parser=section_parser,
            event_list_parser=event_list_parser,
            intersect=intersect,
            scene_event_detection=scene_event_detection,
        ).start()

    def _create_datastore(self) -> Datastore:
        """
        Build all required objects and inject them where necessary
        """,
        track_repository = self._create_track_repository()
        track_parser = self._create_track_parser(track_repository)
        section_parser = self._create_section_parser()
        event_list_parser = self._create_event_list_parser()
        video_parser = OttrkVideoParser(MoviepyVideoReader())
        return Datastore(
            track_repository,
            track_parser,
            section_parser,
            event_list_parser,
            video_parser,
        )

    def _create_track_repository(self) -> TrackRepository:
        return TrackRepository()

    def _create_track_parser(self, track_repository: TrackRepository) -> TrackParser:
        return OttrkParser(
            CalculateTrackClassificationByMaxConfidence(), track_repository
        )

    def _create_section_parser(self) -> SectionParser:
        return OtsectionParser()

    def _create_event_list_parser(self) -> EventListParser:
        return OtEventListParser()

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

    def _create_intersect(self) -> RunIntersect:
        return RunIntersect(
            intersect_implementation=ShapelyIntersectImplementationAdapter(
                ShapelyIntersector()
            ),
        )

    def _create_scene_event_detection(self) -> RunSceneEventDetection:
        return RunSceneEventDetection(SceneActionDetector(SceneEventBuilder()))
