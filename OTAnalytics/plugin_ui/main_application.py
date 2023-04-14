from typing import Any

from OTAnalytics.adapter_intersect.intersect import (
    ShapelyIntersectImplementationAdapter,
)
from OTAnalytics.application.analysis import RunIntersect
from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.datastore import (
    Datastore,
    EventListParser,
    SectionParser,
    TrackParser,
)
from OTAnalytics.application.state import (
    SectionState,
    TrackImageUpdater,
    TrackState,
    TrackViewState,
)
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
from OTAnalytics.plugin_video_processing.video_reader import MoviepyVideoReader


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
        from plugin_ui.customtkinter_gui.gui import OTAnalyticsGui

        application = OTAnalyticsApplication(**self.build_dependencies())
        OTAnalyticsGui(application).start()

    def start_cli(self, cli_args: CliArguments) -> None:
        OTAnalyticsCli(cli_args, **self.build_cli_dependencies()).start()

    def build_dependencies(self) -> dict[str, Any]:
        datastore = self._create_datastore()
        return {
            "datastore": datastore,
            "track_state": self._create_track_state(),
            "track_view_state": self._create_track_view_state(datastore),
            "section_state": self._create_section_state(),
            "intersect": self._create_intersect(),
        }

    def build_cli_dependencies(self) -> dict[str, Any]:
        return {
            "track_parser": self._create_track_parser(self._create_track_repository()),
            "section_parser": self._create_section_parser(),
            "event_list_parser": self._create_event_list_parser(),
            "intersect": self._create_intersect(),
        }

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
