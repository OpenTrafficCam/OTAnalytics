from OTAnalytics.adapter_intersect.intersect import (
    ShapelyIntersectImplementationAdapter,
)
from OTAnalytics.application.analysis import RunIntersect, RunSceneEventDetection
from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.datastore import (
    Datastore,
    EventListParser,
    FlowParser,
    TrackParser,
)
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.plotting import LayeredPlotter
from OTAnalytics.application.state import (
    Plotter,
    SectionState,
    TrackImageUpdater,
    TrackPropertiesUpdater,
    TracksMetadata,
    TrackState,
    TrackViewState,
)
from OTAnalytics.domain.event import SceneEventBuilder
from OTAnalytics.domain.filter import FilterElementSettingRestorer
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.section import SectionRepository
from OTAnalytics.domain.track import (
    CalculateTrackClassificationByMaxConfidence,
    TrackRepository,
)
from OTAnalytics.plugin_filter.dataframe_filter import DataFrameFilterBuilder
from OTAnalytics.plugin_intersect.intersect import ShapelyIntersector
from OTAnalytics.plugin_intersect_parallelization.multiprocessing import (
    MultiprocessingIntersectParallelization,
)
from OTAnalytics.plugin_parser.otvision_parser import (
    OtEventListParser,
    OtFlowParser,
    OttrkParser,
    OttrkVideoParser,
)
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    MatplotlibTrackPlotter,
    PandasTrackProvider,
    PlotterPrototype,
    SectionGeometryPlotter,
    TrackBackgroundPlotter,
    TrackGeometryPlotter,
    TrackStartEndPointPlotter,
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
        from OTAnalytics.plugin_ui.customtkinter_gui.dummy_viewmodel import (
            DummyViewModel,
        )
        from OTAnalytics.plugin_ui.customtkinter_gui.gui import OTAnalyticsGui

        track_repository = self._create_track_repository()
        datastore = self._create_datastore(track_repository)
        track_state = self._create_track_state()
        track_view_state = self._create_track_view_state(datastore)
        section_state = self._create_section_state()
        intersect = self._create_intersect()
        scene_event_detection = self._create_scene_event_detection()
        tracks_metadata = self._create_tracks_metadata(track_repository)
        filter_element_settings_restorer = (
            self._create_filter_element_setting_restorer()
        )

        application = OTAnalyticsApplication(
            datastore=datastore,
            track_state=track_state,
            track_view_state=track_view_state,
            section_state=section_state,
            intersect=intersect,
            scene_event_detection=scene_event_detection,
            tracks_metadata=tracks_metadata,
            filter_element_setting_restorer=filter_element_settings_restorer,
        )
        flow_parser: FlowParser = application._datastore._flow_parser
        dummy_viewmodel = DummyViewModel(application, flow_parser)
        application.connect_observers()
        OTAnalyticsGui(dummy_viewmodel).start()

    def start_cli(self, cli_args: CliArguments) -> None:
        track_parser = self._create_track_parser(self._create_track_repository())
        flow_parser = self._create_flow_parser()
        event_list_parser = self._create_event_list_parser()
        intersect = self._create_intersect()
        scene_event_detection = self._create_scene_event_detection()
        OTAnalyticsCli(
            cli_args,
            track_parser=track_parser,
            flow_parser=flow_parser,
            event_list_parser=event_list_parser,
            intersect=intersect,
            scene_event_detection=scene_event_detection,
        ).start()

    def _create_datastore(self, track_repository: TrackRepository) -> Datastore:
        """
        Build all required objects and inject them where necessary

        Args:
            track_repository (TrackRepository): the track repository to inject
        """
        track_parser = self._create_track_parser(track_repository)
        section_repository = self._create_section_repository()
        flow_parser = self._create_flow_parser()
        flow_repository = self._create_flow_repository()
        event_list_parser = self._create_event_list_parser()
        video_parser = OttrkVideoParser(MoviepyVideoReader())
        return Datastore(
            track_repository,
            track_parser,
            section_repository,
            flow_parser,
            flow_repository,
            event_list_parser,
            video_parser,
        )

    def _create_track_repository(self) -> TrackRepository:
        return TrackRepository()

    def _create_track_parser(self, track_repository: TrackRepository) -> TrackParser:
        return OttrkParser(
            CalculateTrackClassificationByMaxConfidence(), track_repository
        )

    def _create_section_repository(self) -> SectionRepository:
        return SectionRepository()

    def _create_flow_parser(self) -> FlowParser:
        return OtFlowParser()

    def _create_flow_repository(self) -> FlowRepository:
        return FlowRepository()

    def _create_event_list_parser(self) -> EventListParser:
        return OtEventListParser()

    def _create_track_state(self) -> TrackState:
        return TrackState()

    def _create_track_view_state(self, datastore: Datastore) -> TrackViewState:
        state = TrackViewState()
        background_image_plotter = TrackBackgroundPlotter(datastore)
        dataframe_filter_builder = self._create_dataframe_filter_builder()
        pandas_data_provider = PandasTrackProvider(
            datastore, state, dataframe_filter_builder
        )
        track_geometry_plotter = self._create_track_geometry_plotter(
            state,
            pandas_data_provider,
        )
        track_start_end_point_plotter = self._create_track_start_end_point_plotter(
            state,
            pandas_data_provider,
        )
        section_plotter = PlotterPrototype(
            state, MatplotlibTrackPlotter(SectionGeometryPlotter(datastore))
        )
        layers = [
            background_image_plotter,
            track_geometry_plotter,
            track_start_end_point_plotter,
            section_plotter,
        ]
        plotter = LayeredPlotter(layers=layers)
        properties_updater = TrackPropertiesUpdater(datastore, state)
        image_updater = TrackImageUpdater(datastore, state, plotter)
        datastore.register_tracks_observer(properties_updater)
        datastore.register_tracks_observer(image_updater)
        return state

    def _create_track_geometry_plotter(
        self,
        state: TrackViewState,
        pandas_data_provider: PandasTrackProvider,
    ) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            TrackGeometryPlotter(pandas_data_provider),
        )
        return PlotterPrototype(state, track_plotter)

    def _create_track_start_end_point_plotter(
        self,
        state: TrackViewState,
        pandas_data_provider: PandasTrackProvider,
    ) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            TrackStartEndPointPlotter(pandas_data_provider),
        )
        return PlotterPrototype(state, track_plotter)

    def _create_section_state(self) -> SectionState:
        return SectionState()

    def _create_intersect(self) -> RunIntersect:
        return RunIntersect(
            intersect_implementation=ShapelyIntersectImplementationAdapter(
                ShapelyIntersector()
            ),
            intersect_parallelizer=MultiprocessingIntersectParallelization(),
        )

    def _create_scene_event_detection(self) -> RunSceneEventDetection:
        return RunSceneEventDetection(SceneActionDetector(SceneEventBuilder()))

    def _create_tracks_metadata(
        self, track_repository: TrackRepository
    ) -> TracksMetadata:
        return TracksMetadata(track_repository)

    def _create_dataframe_filter_builder(self) -> DataFrameFilterBuilder:
        return DataFrameFilterBuilder()

    def _create_filter_element_setting_restorer(self) -> FilterElementSettingRestorer:
        return FilterElementSettingRestorer()
