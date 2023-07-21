from typing import Sequence

from OTAnalytics.adapter_intersect.intersect import (
    ShapelyIntersectImplementationAdapter,
)
from OTAnalytics.application.analysis.intersect import (
    RunIntersect,
    RunSceneEventDetection,
)
from OTAnalytics.application.analysis.traffic_counting import RoadUserAssigner
from OTAnalytics.application.application import (
    OTAnalyticsApplication,
    TracksAssignedToSelectedFlows,
    TracksIntersectingSelectedSections,
    TracksNotIntersectingSelection,
)
from OTAnalytics.application.datastore import (
    Datastore,
    EventListParser,
    FlowParser,
    TrackParser,
    TrackToVideoRepository,
)
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.plotting import (
    LayeredPlotter,
    PlottingLayer,
    TrackBackgroundPlotter,
)
from OTAnalytics.application.state import (
    ActionState,
    FlowState,
    Plotter,
    SectionState,
    SelectedVideoUpdate,
    TrackImageUpdater,
    TrackPropertiesUpdater,
    TracksMetadata,
    TrackState,
    TrackViewState,
)
from OTAnalytics.domain.event import EventRepository, SceneEventBuilder
from OTAnalytics.domain.filter import FilterElementSettingRestorer
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.section import SectionRepository
from OTAnalytics.domain.track import (
    CalculateTrackClassificationByMaxConfidence,
    TrackRepository,
)
from OTAnalytics.domain.video import VideoRepository
from OTAnalytics.plugin_filter.dataframe_filter import DataFrameFilterBuilder
from OTAnalytics.plugin_intersect.intersect import ShapelyIntersector
from OTAnalytics.plugin_intersect_parallelization.multiprocessing import (
    MultiprocessingIntersectParallelization,
)
from OTAnalytics.plugin_parser.export import SimpleExporterFactory
from OTAnalytics.plugin_parser.otvision_parser import (
    CachedVideoParser,
    OtConfigParser,
    OtEventListParser,
    OtFlowParser,
    OttrkParser,
    OttrkVideoParser,
    SimpleVideoParser,
)
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    CachedPandasTrackProvider,
    FilterById,
    MatplotlibTrackPlotter,
    PandasDataFrameProvider,
    PandasTracksOffsetProvider,
    PlotterPrototype,
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
        track_view_state = self._create_track_view_state()
        section_state = self._create_section_state()
        flow_state = self._create_flow_state()
        road_user_assigner = RoadUserAssigner()

        pandas_data_provider = self._create_pandas_data_provider(
            datastore, track_view_state
        )
        layers = self._create_layers(
            datastore,
            track_view_state,
            flow_state,
            section_state,
            pandas_data_provider,
            road_user_assigner,
        )
        plotter = LayeredPlotter(layers=layers)
        properties_updater = TrackPropertiesUpdater(datastore, track_view_state)
        track_view_state.selected_videos.register(properties_updater.notify_videos)
        image_updater = TrackImageUpdater(
            datastore, track_view_state, section_state, flow_state, plotter
        )
        selected_video_updater = SelectedVideoUpdate(datastore, track_view_state)

        intersect = self._create_intersect()
        scene_event_detection = self._create_scene_event_detection()
        tracks_metadata = self._create_tracks_metadata(track_repository)
        action_state = self._create_action_state()
        filter_element_settings_restorer = (
            self._create_filter_element_setting_restorer()
        )

        application = OTAnalyticsApplication(
            datastore=datastore,
            track_state=track_state,
            track_view_state=track_view_state,
            section_state=section_state,
            flow_state=flow_state,
            intersect=intersect,
            scene_event_detection=scene_event_detection,
            tracks_metadata=tracks_metadata,
            action_state=action_state,
            filter_element_setting_restorer=filter_element_settings_restorer,
            exporter_factory=SimpleExporterFactory(),
        )
        application.connect_clear_event_repository_observer()
        flow_parser: FlowParser = application._datastore._flow_parser
        dummy_viewmodel = DummyViewModel(application, flow_parser)
        dummy_viewmodel.register_observers()
        application.connect_observers()
        datastore.register_tracks_observer(selected_video_updater)
        datastore.register_tracks_observer(dummy_viewmodel)
        datastore.register_tracks_observer(image_updater)
        datastore.register_video_observer(selected_video_updater)
        datastore.register_section_changed_observer(
            image_updater.notify_section_changed
        )
        for layer in layers:
            layer.register(image_updater.notify_layers)
        OTAnalyticsGui(dummy_viewmodel, layers).start()

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
        event_repository = self._create_event_repository()
        event_list_parser = self._create_event_list_parser()
        video_parser = CachedVideoParser(SimpleVideoParser(MoviepyVideoReader()))
        video_repository = VideoRepository()
        track_to_video_repository = TrackToVideoRepository()
        track_video_parser = OttrkVideoParser(video_parser)
        config_parser = OtConfigParser(
            video_parser=video_parser,
            flow_parser=flow_parser,
        )
        return Datastore(
            track_repository,
            track_parser,
            section_repository,
            flow_parser,
            flow_repository,
            event_repository,
            event_list_parser,
            track_to_video_repository,
            video_repository,
            video_parser,
            track_video_parser,
            config_parser=config_parser,
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

    def _create_event_repository(self) -> EventRepository:
        return EventRepository()

    def _create_event_list_parser(self) -> EventListParser:
        return OtEventListParser()

    def _create_track_state(self) -> TrackState:
        return TrackState()

    def _create_track_view_state(self) -> TrackViewState:
        return TrackViewState()

    def _create_pandas_data_provider(
        self, datastore: Datastore, track_view_state: TrackViewState
    ) -> PandasDataFrameProvider:
        dataframe_filter_builder = self._create_dataframe_filter_builder()
        return PandasTracksOffsetProvider(
            CachedPandasTrackProvider(
                datastore, track_view_state, dataframe_filter_builder
            ),
            track_view_state=track_view_state,
        )

    def _create_track_geometry_plotter(
        self,
        state: TrackViewState,
        pandas_data_provider: PandasDataFrameProvider,
        alpha: float,
        enable_legend: bool,
    ) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            TrackGeometryPlotter(
                pandas_data_provider, alpha=alpha, enable_legend=enable_legend
            ),
        )
        return PlotterPrototype(state, track_plotter)

    def _create_track_start_end_point_plotter(
        self,
        state: TrackViewState,
        pandas_data_provider: PandasDataFrameProvider,
        enable_legend: bool,
    ) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            TrackStartEndPointPlotter(
                pandas_data_provider, enable_legend=enable_legend
            ),
        )
        return PlotterPrototype(state, track_plotter)

    def _create_track_highlight_geometry_plotter(
        self,
        state: TrackViewState,
        tracks_intersecting_selected_sections: TracksIntersectingSelectedSections,
        pandas_track_provider: PandasDataFrameProvider,
        enable_legend: bool,
    ) -> Plotter:
        filter_by_id = FilterById(
            pandas_track_provider, id_filter=tracks_intersecting_selected_sections
        )
        return self._create_track_geometry_plotter(
            state, filter_by_id, alpha=1, enable_legend=enable_legend
        )

    def _create_tracks_intersecting_selected_sections(
        self,
        section_state: SectionState,
        event_repository: EventRepository,
    ) -> TracksIntersectingSelectedSections:
        return TracksIntersectingSelectedSections(section_state, event_repository)

    def _create_track_highlight_geometry_plotter_not_intersecting(
        self,
        state: TrackViewState,
        tracks_not_intersecting_sections: TracksNotIntersectingSelection,
        pandas_track_provider: PandasDataFrameProvider,
        enable_legend: bool,
    ) -> Plotter:
        filter_by_id = FilterById(
            pandas_track_provider, id_filter=tracks_not_intersecting_sections
        )
        return self._create_track_geometry_plotter(
            state, filter_by_id, alpha=1, enable_legend=enable_legend
        )

    def _create_start_end_point_tracks_intersecting_sections_plotter(
        self,
        state: TrackViewState,
        tracks_intersecting_sections: TracksIntersectingSelectedSections,
        pandas_track_provider: PandasDataFrameProvider,
        enable_legend: bool,
    ) -> Plotter:
        filter_by_id = FilterById(
            pandas_track_provider, id_filter=tracks_intersecting_sections
        )

        return self._create_track_start_end_point_plotter(
            state, filter_by_id, enable_legend=enable_legend
        )

    def _create_start_end_point_tracks_not_intersecting_sections_plotter(
        self,
        state: TrackViewState,
        tracks_not_intersecting_sections: TracksNotIntersectingSelection,
        pandas_track_provider: PandasDataFrameProvider,
        enable_legend: bool,
    ) -> Plotter:
        filter_by_id = FilterById(
            pandas_track_provider, id_filter=tracks_not_intersecting_sections
        )

        return self._create_track_start_end_point_plotter(
            state, filter_by_id, enable_legend=enable_legend
        )

    def _create_highlight_tracks_assigned_to_flow(
        self,
        state: TrackViewState,
        pandas_track_provider: PandasDataFrameProvider,
        tracks_assigned_to_flow: TracksAssignedToSelectedFlows,
        enable_legend: bool,
    ) -> Plotter:
        filter_by_id = FilterById(
            pandas_track_provider, id_filter=tracks_assigned_to_flow
        )
        return self._create_track_geometry_plotter(
            state, filter_by_id, alpha=1, enable_legend=enable_legend
        )

    def _create_highlight_tracks_not_assigned_to_flow(
        self,
        state: TrackViewState,
        pandas_track_provider: PandasDataFrameProvider,
        tracks_assigned_to_flow: TracksAssignedToSelectedFlows,
        track_repository: TrackRepository,
        enable_legend: bool,
    ) -> Plotter:
        tracks_not_assigned_to_flow = TracksNotIntersectingSelection(
            tracks_assigned_to_flow, track_repository
        )
        filter_by_id = FilterById(
            pandas_track_provider, id_filter=tracks_not_assigned_to_flow
        )
        return self._create_track_geometry_plotter(
            state, filter_by_id, alpha=1, enable_legend=enable_legend
        )

    def _create_layers(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
        flow_state: FlowState,
        section_state: SectionState,
        pandas_data_provider: PandasDataFrameProvider,
        road_user_assigner: RoadUserAssigner,
    ) -> Sequence[PlottingLayer]:
        background_image_plotter = TrackBackgroundPlotter(track_view_state, datastore)

        track_geometry_plotter = self._create_track_geometry_plotter(
            track_view_state, pandas_data_provider, alpha=0.2, enable_legend=True
        )
        tracks_intersecting_sections = TracksIntersectingSelectedSections(
            section_state, datastore._event_repository
        )
        tracks_not_intersecting_sections = TracksNotIntersectingSelection(
            tracks_intersecting_sections, datastore._track_repository
        )

        highlight_tracks_intersecting_sections = (
            self._create_track_highlight_geometry_plotter(
                track_view_state,
                tracks_intersecting_sections,
                pandas_data_provider,
                enable_legend=False,
            )
        )
        highlight_tracks_not_intersecting_sections = (
            self._create_track_highlight_geometry_plotter_not_intersecting(
                track_view_state,
                tracks_not_intersecting_sections,
                pandas_data_provider,
                enable_legend=False,
            )
        )
        start_end_points_tracks_intersecting_sections = (
            self._create_start_end_point_tracks_intersecting_sections_plotter(
                track_view_state,
                tracks_intersecting_sections,
                pandas_data_provider,
                enable_legend=False,
            )
        )
        start_end_points_tracks_not_intersecting_sections = (
            self._create_start_end_point_tracks_not_intersecting_sections_plotter(
                track_view_state,
                tracks_not_intersecting_sections,
                pandas_data_provider,
                enable_legend=False,
            )
        )
        track_start_end_point_plotter = self._create_track_start_end_point_plotter(
            track_view_state, pandas_data_provider, enable_legend=False
        )
        tracks_assigned_to_flow = TracksAssignedToSelectedFlows(
            road_user_assigner,
            datastore._event_repository,
            datastore._flow_repository,
            flow_state,
        )
        highlight_tracks_assigned_to_flow = (
            self._create_highlight_tracks_assigned_to_flow(
                track_view_state,
                pandas_data_provider,
                tracks_assigned_to_flow,
                enable_legend=False,
            )
        )
        highlight_tracks_not_assigned_to_flow = (
            self._create_highlight_tracks_not_assigned_to_flow(
                track_view_state,
                pandas_data_provider,
                tracks_assigned_to_flow,
                datastore._track_repository,
                enable_legend=False,
            )
        )
        background = PlottingLayer("Background", background_image_plotter, enabled=True)
        all_tracks_layer = PlottingLayer(
            "Show all tracks", track_geometry_plotter, enabled=True
        )
        highlight_tracks_intersecting_sections_layer = PlottingLayer(
            "Highlight tracks intersecting sections",
            highlight_tracks_intersecting_sections,
            enabled=False,
        )
        highlight_tracks_not_intersecting_sections_layer = PlottingLayer(
            "Highlight tracks not intersecting sections",
            highlight_tracks_not_intersecting_sections,
            enabled=False,
        )
        start_end_points_tracks_intersecting_sections_layer = PlottingLayer(
            "Show start and end point of tracks intersecting sections",
            start_end_points_tracks_intersecting_sections,
            enabled=False,
        )
        start_end_points_tracks_not_intersecting_sections_layer = PlottingLayer(
            "Show start and end point of tracks not intersecting sections",
            start_end_points_tracks_not_intersecting_sections,
            enabled=False,
        )
        start_end_point_layer = PlottingLayer(
            "Show start and end point", track_start_end_point_plotter, enabled=False
        )
        highlight_tracks_assigned_to_flow_layer = PlottingLayer(
            "Highlight tracks assigned to flow",
            highlight_tracks_assigned_to_flow,
            enabled=False,
        )
        highlight_tracks_not_assigned_to_flow_layer = PlottingLayer(
            "Highlight tracks not assigned to flow",
            highlight_tracks_not_assigned_to_flow,
            enabled=False,
        )

        return [
            background,
            all_tracks_layer,
            highlight_tracks_intersecting_sections_layer,
            highlight_tracks_not_intersecting_sections_layer,
            start_end_point_layer,
            start_end_points_tracks_intersecting_sections_layer,
            start_end_points_tracks_not_intersecting_sections_layer,
            highlight_tracks_assigned_to_flow_layer,
            highlight_tracks_not_assigned_to_flow_layer,
        ]

    def _create_section_state(self) -> SectionState:
        return SectionState()

    def _create_flow_state(self) -> FlowState:
        return FlowState()

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

    def _create_action_state(self) -> ActionState:
        return ActionState()

    def _create_dataframe_filter_builder(self) -> DataFrameFilterBuilder:
        return DataFrameFilterBuilder()

    def _create_filter_element_setting_restorer(self) -> FilterElementSettingRestorer:
        return FilterElementSettingRestorer()
