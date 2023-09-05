import logging
from typing import Callable, Optional, Sequence

from OTAnalytics.adapter_ui.default_values import TRACK_LENGTH_LIMIT
from OTAnalytics.application.analysis.intersect import (
    RunIntersect,
    TracksIntersectingSections,
)
from OTAnalytics.application.analysis.traffic_counting import (
    ExportTrafficCounting,
    FilterBySectionEnterEvent,
    RoadUserAssigner,
    SimpleRoadUserAssigner,
    SimpleTaggerFactory,
)
from OTAnalytics.application.analysis.traffic_counting_specification import ExportCounts
from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.datastore import (
    Datastore,
    EventListParser,
    FlowParser,
    TrackParser,
    TrackToVideoRepository,
)
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.logger import logger, setup_logger
from OTAnalytics.application.plotting import (
    CachedPlotter,
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
from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.create_events import (
    CreateEvents,
    CreateIntersectionEvents,
    SimpleCreateIntersectionEvents,
    SimpleCreateSceneEvents,
)
from OTAnalytics.application.use_cases.event_repository import AddEvents, ClearAllEvents
from OTAnalytics.application.use_cases.flow_repository import AddFlow, ClearAllFlows
from OTAnalytics.application.use_cases.generate_flows import (
    ArrowFlowNameGenerator,
    CrossProductFlowGenerator,
    FilterExisting,
    FilterSameSection,
    FlowIdGenerator,
    GenerateFlows,
    RepositoryFlowIdGenerator,
)
from OTAnalytics.application.use_cases.highlight_intersections import (
    TracksAssignedToGivenFlows,
    TracksAssignedToSelectedFlows,
    TracksIntersectingGivenSections,
    TracksIntersectingSelectedSections,
    TracksNotIntersectingSelection,
    TracksOverlapOccurrenceWindow,
)
from OTAnalytics.application.use_cases.load_otflow import LoadOtflow
from OTAnalytics.application.use_cases.reset_project_config import ResetProjectConfig
from OTAnalytics.application.use_cases.section_repository import (
    AddSection,
    ClearAllSections,
    GetSectionsById,
)
from OTAnalytics.application.use_cases.start_new_project import StartNewProject
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    ClearAllTracks,
    GetAllTrackFiles,
    GetAllTracks,
)
from OTAnalytics.application.use_cases.track_to_video_repository import (
    ClearAllTrackToVideos,
)
from OTAnalytics.application.use_cases.update_project import ProjectUpdater
from OTAnalytics.application.use_cases.video_repository import ClearAllVideos
from OTAnalytics.domain.event import EventRepository, SceneEventBuilder
from OTAnalytics.domain.filter import FilterElementSettingRestorer
from OTAnalytics.domain.flow import FlowId, FlowRepository
from OTAnalytics.domain.intersect import IntersectImplementation
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.section import SectionId, SectionRepository
from OTAnalytics.domain.track import (
    CalculateTrackClassificationByMaxConfidence,
    TrackFileRepository,
    TrackIdProvider,
    TrackRepository,
)
from OTAnalytics.domain.video import VideoRepository
from OTAnalytics.plugin_filter.dataframe_filter import DataFrameFilterBuilder
from OTAnalytics.plugin_intersect.shapely.intersect import ShapelyIntersector
from OTAnalytics.plugin_intersect.shapely.mapping import ShapelyMapper
from OTAnalytics.plugin_intersect.simple_intersect import (
    SimpleRunIntersect,
    SimpleTracksIntersectingSections,
)
from OTAnalytics.plugin_intersect_parallelization.multiprocessing import (
    MultiprocessingIntersectParallelization,
)
from OTAnalytics.plugin_parser.export import (
    FillZerosExporterFactory,
    SimpleExporterFactory,
)
from OTAnalytics.plugin_parser.otvision_parser import (
    CachedVideoParser,
    OtConfigParser,
    OtEventListParser,
    OtFlowParser,
    OttrkParser,
    OttrkVideoParser,
    SimpleVideoParser,
)
from OTAnalytics.plugin_progress.tqdm_progressbar import TqdmBuilder
from OTAnalytics.plugin_prototypes.eventlist_exporter.eventlist_exporter import (
    AVAILABLE_EVENTLIST_EXPORTERS,
)
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    CachedPandasTrackProvider,
    ColorPaletteProvider,
    FilterByClassification,
    FilterById,
    FilterByOccurrence,
    FlowLayerPlotter,
    FlowListObserverWrapper,
    MatplotlibTrackPlotter,
    PandasDataFrameProvider,
    PandasTracksOffsetProvider,
    PlotterPrototype,
    SectionLayerPlotter,
    SectionListObserverWrapper,
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
        self._setup_logger(cli_args.debug)

        if cli_args.start_cli:
            try:
                self.start_cli(cli_args)
            except CliParseError as e:
                logger().exception(e, exc_info=True)
        else:
            self.start_gui()

    def _build_cli_argument_parser(self) -> CliArgumentParser:
        return CliArgumentParser()

    def _setup_logger(self, debug: bool) -> None:
        if debug:
            setup_logger(logging.DEBUG)
        else:
            setup_logger(logging.INFO)

    def start_gui(self) -> None:
        from OTAnalytics.plugin_ui.customtkinter_gui.dummy_viewmodel import (
            DummyViewModel,
        )
        from OTAnalytics.plugin_ui.customtkinter_gui.gui import (
            ModifiedCTk,
            OTAnalyticsGui,
        )
        from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_progress import (
            PullingProgressbarBuilder,
            PullingProgressbarPopupBuilder,
        )

        pulling_progressbar_popup_builder = PullingProgressbarPopupBuilder()
        pulling_progressbar_builder = PullingProgressbarBuilder(
            pulling_progressbar_popup_builder
        )

        track_repository = self._create_track_repository()
        track_file_repository = self._create_track_file_repository()
        section_repository = self._create_section_repository()
        flow_repository = self._create_flow_repository()
        event_repository = self._create_event_repository()
        datastore = self._create_datastore(
            track_repository,
            track_file_repository,
            section_repository,
            flow_repository,
            event_repository,
            pulling_progressbar_builder,
        )
        track_state = self._create_track_state()
        track_view_state = self._create_track_view_state()
        section_state = self._create_section_state()
        flow_state = self._create_flow_state()
        road_user_assigner = FilterBySectionEnterEvent(SimpleRoadUserAssigner())

        pandas_data_provider = self._create_pandas_data_provider(
            datastore, track_view_state, pulling_progressbar_builder
        )
        color_palette_provider = ColorPaletteProvider()
        layers = self._create_layers(
            datastore,
            track_view_state,
            flow_state,
            section_state,
            pandas_data_provider,
            road_user_assigner,
            color_palette_provider,
        )
        plotter = LayeredPlotter(layers=layers)
        properties_updater = TrackPropertiesUpdater(datastore, track_view_state)
        image_updater = TrackImageUpdater(
            datastore, track_view_state, section_state, flow_state, plotter
        )
        track_view_state.selected_videos.register(properties_updater.notify_videos)
        track_view_state.selected_videos.register(image_updater.notify_video)
        selected_video_updater = SelectedVideoUpdate(datastore, track_view_state)

        tracks_metadata = self._create_tracks_metadata(track_repository)
        # TODO: Should not register to tracks_metadata._classifications but to
        # TODO: ottrk metadata detection classes
        tracks_metadata._classifications.register(
            observer=color_palette_provider.update
        )
        action_state = self._create_action_state()
        filter_element_settings_restorer = (
            self._create_filter_element_setting_restorer()
        )
        get_all_track_files = self._create_get_all_track_files(track_file_repository)
        generate_flows = self._create_flow_generator(
            section_repository, flow_repository
        )
        add_events = AddEvents(event_repository)
        clear_all_events = ClearAllEvents(event_repository)
        get_all_tracks = GetAllTracks(track_repository)
        clear_all_tracks = ClearAllTracks(track_repository)
        clear_all_sections = ClearAllSections(section_repository)
        clear_all_flows = ClearAllFlows(flow_repository)
        add_section = AddSection(section_repository)
        add_flow = AddFlow(flow_repository)
        clear_all_videos = ClearAllVideos(datastore._video_repository)
        clear_all_track_to_videos = ClearAllTrackToVideos(
            datastore._track_to_video_repository
        )
        create_events = self._create_use_case_create_events(
            section_repository, clear_all_events, get_all_tracks, add_events
        )
        intersect_tracks_with_sections = (
            self._create_use_case_create_intersection_events(
                section_repository, get_all_tracks, add_events
            )
        )
        export_counts = self._create_export_counts(
            event_repository, flow_repository, track_repository
        )
        load_otflow = self._create_use_case_load_otflow(
            clear_all_sections,
            clear_all_flows,
            clear_all_events,
            datastore._flow_parser,
            add_section,
            add_flow,
        )
        clear_repositories = self._create_use_case_clear_all_repositories(
            clear_all_events,
            clear_all_flows,
            clear_all_sections,
            clear_all_track_to_videos,
            clear_all_tracks,
            clear_all_videos,
        )
        project_updater = self._create_project_updater(datastore)
        reset_project_config = self._create_reset_project_config(project_updater)
        start_new_project = self._create_use_case_start_new_project(
            clear_repositories, reset_project_config, track_view_state
        )
        application = OTAnalyticsApplication(
            datastore,
            track_state,
            track_view_state,
            section_state,
            flow_state,
            tracks_metadata,
            action_state,
            filter_element_settings_restorer,
            get_all_track_files,
            generate_flows,
            intersect_tracks_with_sections,
            export_counts,
            create_events,
            load_otflow,
            add_section,
            add_flow,
            clear_all_events,
            start_new_project,
            project_updater,
        )
        application.connect_clear_event_repository_observer()
        flow_parser: FlowParser = application._datastore._flow_parser
        name_generator = ArrowFlowNameGenerator()
        dummy_viewmodel = DummyViewModel(
            application,
            flow_parser,
            name_generator,
            event_list_export_formats=AVAILABLE_EVENTLIST_EXPORTERS,
        )
        dummy_viewmodel.register_observers()
        application.connect_observers()
        datastore.register_tracks_observer(selected_video_updater)
        datastore.register_tracks_observer(dummy_viewmodel)
        datastore.register_tracks_observer(image_updater)
        datastore.register_video_observer(selected_video_updater)
        datastore.register_section_changed_observer(
            image_updater.notify_section_changed
        )
        start_new_project.register(dummy_viewmodel.on_start_new_project)

        for layer in layers:
            layer.register(image_updater.notify_layers)
        main_window = ModifiedCTk(dummy_viewmodel)
        pulling_progressbar_popup_builder.add_widget(main_window)
        OTAnalyticsGui(main_window, dummy_viewmodel, layers).start()

    def start_cli(self, cli_args: CliArguments) -> None:
        track_repository = self._create_track_repository()
        track_file_repository = self._create_track_file_repository()
        section_repository = self._create_section_repository()
        track_parser = self._create_track_parser(
            track_repository, track_file_repository
        )
        flow_parser = self._create_flow_parser()
        event_list_parser = self._create_event_list_parser()
        event_repository = self._create_event_repository()
        add_section = AddSection(section_repository)
        add_events = AddEvents(event_repository)
        get_all_tracks = GetAllTracks(track_repository)
        clear_all_events = ClearAllEvents(event_repository)
        create_events = self._create_use_case_create_events(
            section_repository, clear_all_events, get_all_tracks, add_events
        )
        add_all_tracks = AddAllTracks(track_repository)
        clear_all_tracks = ClearAllTracks(track_repository)
        OTAnalyticsCli(
            cli_args,
            track_parser=track_parser,
            flow_parser=flow_parser,
            event_list_parser=event_list_parser,
            event_repository=event_repository,
            add_section=add_section,
            create_events=create_events,
            add_all_tracks=add_all_tracks,
            clear_all_tracks=clear_all_tracks,
            progressbar=TqdmBuilder(),
        ).start()

    def _create_datastore(
        self,
        track_repository: TrackRepository,
        track_file_repository: TrackFileRepository,
        section_repository: SectionRepository,
        flow_repository: FlowRepository,
        event_repository: EventRepository,
        progressbar_builder: ProgressbarBuilder,
    ) -> Datastore:
        """
        Build all required objects and inject them where necessary

        Args:
            track_repository (TrackRepository): the track repository to inject
            progressbar_builder (ProgressbarBuilder): the progressbar builder to inject
        """
        track_parser = self._create_track_parser(
            track_repository, track_file_repository
        )
        flow_parser = self._create_flow_parser()
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
            progressbar_builder,
            config_parser=config_parser,
        )

    def _create_track_repository(self) -> TrackRepository:
        return TrackRepository()

    def _create_track_parser(
        self,
        track_repository: TrackRepository,
        track_file_repository: TrackFileRepository,
    ) -> TrackParser:
        return OttrkParser(
            CalculateTrackClassificationByMaxConfidence(),
            track_repository,
            track_file_repository,
            track_length_limit=TRACK_LENGTH_LIMIT,
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

    def _wrap_plotter_with_cache(
        self,
        other: Plotter,
        datastore: Datastore,
        tracks: bool,
        sections: bool,
        flows: bool,
    ) -> Plotter:
        cached_plotter: CachedPlotter = CachedPlotter(other, subjects=[])
        invalidate = cached_plotter.invalidate_cache

        if tracks:
            track_repo = datastore._track_repository
            track_repo.observers.register(invalidate)

        if sections:
            section_repo = datastore._section_repository
            section_repo.register_sections_observer(
                SectionListObserverWrapper(invalidate)
            )
            section_repo._section_content_observers.register(invalidate)

        if flows:
            flow_repo = datastore._flow_repository
            flow_repo.register_flows_observer(FlowListObserverWrapper(invalidate))
            flow_repo._flow_content_observers.register(invalidate)

        return cached_plotter

    def _create_pandas_data_provider(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
        progressbar: ProgressbarBuilder,
    ) -> PandasDataFrameProvider:
        dataframe_filter_builder = self._create_dataframe_filter_builder()
        return PandasTracksOffsetProvider(
            CachedPandasTrackProvider(
                datastore, track_view_state, dataframe_filter_builder, progressbar
            ),
            track_view_state=track_view_state,
        )

    def _create_track_geometry_plotter(
        self,
        state: TrackViewState,
        pandas_data_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
        alpha: float,
        enable_legend: bool,
    ) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            TrackGeometryPlotter(
                pandas_data_provider,
                color_palette_provider,
                alpha=alpha,
                enable_legend=enable_legend,
            ),
        )
        return PlotterPrototype(state, track_plotter)

    def _create_track_start_end_point_data_provider(
        self,
        state: TrackViewState,
        pandas_data_provider: PandasDataFrameProvider,
        track_repository: TrackRepository,
        id_filter: Optional[TrackIdProvider] = None,
    ) -> FilterById:
        data_provider = pandas_data_provider
        data_provider = FilterById(
            pandas_data_provider,
            id_filter=TracksOverlapOccurrenceWindow(
                other=id_filter,
                track_repository=track_repository,
                track_view_state=state,
            ),
        )
        return data_provider

    def _create_track_start_end_point_plotter(
        self,
        state: TrackViewState,
        data_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
        enable_legend: bool,
    ) -> Plotter:
        track_plotter = MatplotlibTrackPlotter(
            TrackStartEndPointPlotter(
                data_provider,
                color_palette_provider,
                enable_legend=enable_legend,
            ),
        )
        return PlotterPrototype(state, track_plotter)

    def _create_tracks_intersecting_selected_sections(
        self,
        section_state: SectionState,
        tracks_intersecting_sections: TracksIntersectingSections,
        get_sections_by_id: GetSectionsById,
    ) -> TracksIntersectingSelectedSections:
        return TracksIntersectingSelectedSections(
            section_state, tracks_intersecting_sections, get_sections_by_id
        )

    def _create_tracks_intersecting_sections_filter(
        self,
        pandas_data_provider: PandasDataFrameProvider,
        tracks_intersecting_sections: TracksIntersectingSections,
        get_sections_by_id: GetSectionsById,
    ) -> Callable[[SectionId], PandasDataFrameProvider]:
        return lambda section: FilterById(
            pandas_data_provider,
            TracksIntersectingGivenSections(
                [section], tracks_intersecting_sections, get_sections_by_id
            ),
        )

    def _create_highlight_tracks_intersecting_section_factory(
        self,
        state: TrackViewState,
        pandas_data_provider_factory: Callable[[SectionId], PandasDataFrameProvider],
        color_palette_provider: ColorPaletteProvider,
        alpha: float,
        enable_legend: bool,
    ) -> Callable[[SectionId], Plotter]:
        return lambda section: self._create_track_geometry_plotter(
            state,
            pandas_data_provider_factory(section),
            color_palette_provider,
            alpha,
            enable_legend,
        )

    def _create_cached_section_layer_plotter(
        self,
        plotter_factory: Callable[[SectionId], Plotter],
        section_state: SectionState,
        section_repository: SectionRepository,
        track_repository: TrackRepository,
    ) -> Plotter:
        return SectionLayerPlotter(
            plotter_factory, section_state, section_repository, track_repository
        )

    def _create_track_highlight_geometry_plotter_not_intersecting(
        self,
        state: TrackViewState,
        tracks_not_intersecting_sections: TracksNotIntersectingSelection,
        pandas_track_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
        enable_legend: bool,
    ) -> Plotter:
        filter_by_id = FilterById(
            pandas_track_provider, id_filter=tracks_not_intersecting_sections
        )
        return self._create_track_geometry_plotter(
            state,
            filter_by_id,
            color_palette_provider,
            alpha=1,
            enable_legend=enable_legend,
        )

    def _create_tracks_start_end_point_intersecting_given_sections_filter(
        self,
        state: TrackViewState,
        track_repository: TrackRepository,
        pandas_data_provider: PandasDataFrameProvider,
        tracks_intersecting_sections: TracksIntersectingSections,
        get_sections_by_id: GetSectionsById,
    ) -> Callable[[SectionId], PandasDataFrameProvider]:
        return lambda section: FilterById(
            pandas_data_provider,
            id_filter=TracksOverlapOccurrenceWindow(
                other=TracksIntersectingGivenSections(
                    [section],
                    tracks_intersecting_sections,
                    get_sections_by_id,
                ),
                track_repository=track_repository,
                track_view_state=state,
            ),
        )

    def _create_start_end_point_intersecting_section_factory(
        self,
        state: TrackViewState,
        pandas_data_provider_factory: Callable[[SectionId], PandasDataFrameProvider],
        color_palette_provider: ColorPaletteProvider,
        enable_legend: bool,
    ) -> Callable[[SectionId], Plotter]:
        return lambda section: self._create_track_start_end_point_plotter(
            state,
            pandas_data_provider_factory(section),
            color_palette_provider,
            enable_legend,
        )

    def _create_start_end_point_tracks_not_intersecting_sections_plotter(
        self,
        state: TrackViewState,
        tracks_not_intersecting_sections: TracksNotIntersectingSelection,
        pandas_track_provider: PandasDataFrameProvider,
        track_repository: TrackRepository,
        color_palette_provider: ColorPaletteProvider,
        enable_legend: bool,
    ) -> Plotter:
        return self._create_track_start_end_point_plotter(
            state,
            self._create_track_start_end_point_data_provider(
                state,
                pandas_track_provider,
                track_repository,
                tracks_not_intersecting_sections,
            ),
            color_palette_provider,
            enable_legend,
        )

    def _create_tracks_assigned_to_flows_filter(
        self,
        pandas_data_provider: PandasDataFrameProvider,
        assigner: RoadUserAssigner,
        event_repository: EventRepository,
        flow_repository: FlowRepository,
    ) -> Callable[[FlowId], PandasDataFrameProvider]:
        return lambda flow: FilterById(
            pandas_data_provider,
            TracksAssignedToGivenFlows(
                assigner,
                event_repository,
                flow_repository,
                [flow],
            ),
        )

    def _create_highlight_tracks_assigned_to_flows_factory(
        self,
        state: TrackViewState,
        pandas_data_provider_factory: Callable[[FlowId], PandasDataFrameProvider],
        color_palette_provider: ColorPaletteProvider,
        alpha: float,
        enable_legend: bool,
    ) -> Callable[[FlowId], Plotter]:
        return lambda flow: self._create_track_geometry_plotter(
            state,
            pandas_data_provider_factory(flow),
            color_palette_provider,
            alpha,
            enable_legend,
        )

    def _create_highlight_tracks_assigned_to_flow(
        self,
        plotter_factory: Callable[[FlowId], Plotter],
        flow_state: FlowState,
        flow_repository: FlowRepository,
        track_repository: TrackRepository,
    ) -> Plotter:
        return FlowLayerPlotter(
            plotter_factory, flow_state, flow_repository, track_repository
        )

    def _create_highlight_tracks_not_assigned_to_flow(
        self,
        state: TrackViewState,
        pandas_track_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
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
            state,
            filter_by_id,
            color_palette_provider,
            alpha=1,
            enable_legend=enable_legend,
        )

    def _create_layers(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
        flow_state: FlowState,
        section_state: SectionState,
        pandas_data_provider: PandasDataFrameProvider,
        road_user_assigner: RoadUserAssigner,
        color_palette_provider: ColorPaletteProvider,
    ) -> Sequence[PlottingLayer]:
        background_image_plotter = TrackBackgroundPlotter(track_view_state, datastore)
        data_provider_all_filters = FilterByClassification(
            FilterByOccurrence(
                pandas_data_provider,
                track_view_state,
                self._create_dataframe_filter_builder(),
            ),
            track_view_state,
            self._create_dataframe_filter_builder(),
        )
        data_provider_class_filter = FilterByClassification(
            pandas_data_provider,
            track_view_state,
            self._create_dataframe_filter_builder(),
        )
        track_geometry_plotter = self._create_track_geometry_plotter(
            track_view_state,
            data_provider_all_filters,
            color_palette_provider,
            alpha=0.2,
            enable_legend=True,
        )
        tracks_intersecting_sections = self._create_tracks_intersecting_sections(
            GetAllTracks(datastore._track_repository),
            ShapelyIntersector(),
        )
        tracks_intersecting_selected_sections = (
            self._create_tracks_intersecting_selected_sections(
                section_state,
                tracks_intersecting_sections,
                GetSectionsById(datastore._section_repository),
            )
        )
        tracks_not_intersecting_sections = TracksNotIntersectingSelection(
            tracks_intersecting_selected_sections, datastore._track_repository
        )

        get_sections_by_id = GetSectionsById(datastore._section_repository)
        tracks_intersecting_sections_filter = (
            self._create_tracks_intersecting_sections_filter(
                data_provider_all_filters,
                tracks_intersecting_sections,
                get_sections_by_id,
            )
        )

        highlight_tracks_intersecting_sections = (
            self._create_cached_section_layer_plotter(
                self._create_highlight_tracks_intersecting_section_factory(
                    track_view_state,
                    tracks_intersecting_sections_filter,
                    color_palette_provider,
                    alpha=1,
                    enable_legend=False,
                ),
                section_state,
                datastore._section_repository,
                datastore._track_repository,
            )
        )
        highlight_tracks_not_intersecting_sections = (
            self._create_track_highlight_geometry_plotter_not_intersecting(
                track_view_state,
                tracks_not_intersecting_sections,
                data_provider_all_filters,
                color_palette_provider,
                enable_legend=False,
            )
        )
        start_end_points_intersecting = self._create_cached_section_layer_plotter(
            self._create_start_end_point_intersecting_section_factory(
                track_view_state,
                self._create_tracks_start_end_point_intersecting_given_sections_filter(
                    track_view_state,
                    datastore._track_repository,
                    data_provider_class_filter,
                    tracks_intersecting_sections,
                    get_sections_by_id,
                ),
                color_palette_provider,
                enable_legend=False,
            ),
            section_state,
            datastore._section_repository,
            datastore._track_repository,
        )

        start_end_points_tracks_not_intersecting_sections = (
            self._create_start_end_point_tracks_not_intersecting_sections_plotter(
                track_view_state,
                tracks_not_intersecting_sections,
                data_provider_class_filter,
                datastore._track_repository,
                color_palette_provider,
                enable_legend=False,
            )
        )
        track_start_end_point_plotter = self._create_track_start_end_point_plotter(
            track_view_state,
            self._create_track_start_end_point_data_provider(
                track_view_state,
                data_provider_class_filter,
                datastore._track_repository,
                tracks_not_intersecting_sections,
            ),
            color_palette_provider,
            enable_legend=False,
        )
        tracks_assigned_to_flow = TracksAssignedToSelectedFlows(
            road_user_assigner,
            datastore._event_repository,
            datastore._flow_repository,
            flow_state,
        )

        highlight_tracks_assigned_to_flow = (
            self._create_highlight_tracks_assigned_to_flow(
                self._create_highlight_tracks_assigned_to_flows_factory(
                    track_view_state,
                    self._create_tracks_assigned_to_flows_filter(
                        data_provider_all_filters,
                        road_user_assigner,
                        datastore._event_repository,
                        datastore._flow_repository,
                    ),
                    color_palette_provider,
                    alpha=1,
                    enable_legend=False,
                ),
                flow_state,
                datastore._flow_repository,
                datastore._track_repository,
            )
        )
        highlight_tracks_not_assigned_to_flow = (
            self._create_highlight_tracks_not_assigned_to_flow(
                track_view_state,
                data_provider_all_filters,
                color_palette_provider,
                tracks_assigned_to_flow,
                datastore._track_repository,
                enable_legend=False,
            )
        )
        background = PlottingLayer("Background", background_image_plotter, enabled=True)
        all_tracks_layer = PlottingLayer(
            "Show all tracks",
            self._wrap_plotter_with_cache(
                track_geometry_plotter,
                datastore,
                tracks=True,
                sections=False,
                flows=False,
            ),
            enabled=True,
        )
        highlight_tracks_intersecting_sections_layer = PlottingLayer(
            "Highlight tracks intersecting sections",
            highlight_tracks_intersecting_sections,
            enabled=False,
        )
        highlight_tracks_not_intersecting_sections_layer = PlottingLayer(
            "Highlight tracks not intersecting sections",
            self._wrap_plotter_with_cache(
                highlight_tracks_not_intersecting_sections,
                datastore,
                tracks=True,
                sections=True,
                flows=False,
            ),
            enabled=False,
        )
        start_end_points_tracks_intersecting_sections_layer = PlottingLayer(
            "Show start and end point of tracks intersecting sections",
            start_end_points_intersecting,
            enabled=False,
        )
        start_end_points_tracks_not_intersecting_sections_layer = PlottingLayer(
            "Show start and end point of tracks not intersecting sections",
            self._wrap_plotter_with_cache(
                start_end_points_tracks_not_intersecting_sections,
                datastore,
                tracks=True,
                sections=True,
                flows=False,
            ),
            enabled=False,
        )
        start_end_point_layer = PlottingLayer(
            "Show start and end point",
            self._wrap_plotter_with_cache(
                track_start_end_point_plotter,
                datastore,
                tracks=True,
                sections=False,
                flows=False,
            ),
            enabled=False,
        )
        highlight_tracks_assigned_to_flow_layer = PlottingLayer(
            "Highlight tracks assigned to flow",
            highlight_tracks_assigned_to_flow,
            enabled=False,
        )
        highlight_tracks_not_assigned_to_flow_layer = PlottingLayer(
            "Highlight tracks not assigned to flow",
            self._wrap_plotter_with_cache(
                highlight_tracks_not_assigned_to_flow,
                datastore,
                tracks=True,
                sections=True,
                flows=True,
            ),
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

    def _create_get_all_track_files(
        self, track_file_repository: TrackFileRepository
    ) -> GetAllTrackFiles:
        return GetAllTrackFiles(track_file_repository)

    def _create_flow_generator(
        self, section_repository: SectionRepository, flow_repository: FlowRepository
    ) -> GenerateFlows:
        id_generator: FlowIdGenerator = RepositoryFlowIdGenerator(flow_repository)
        name_generator = ArrowFlowNameGenerator()
        flow_generator = CrossProductFlowGenerator(
            id_generator=id_generator,
            name_generator=name_generator,
            predicate=FilterSameSection().and_then(FilterExisting(flow_repository)),
        )
        return GenerateFlows(
            section_repository=section_repository,
            flow_repository=flow_repository,
            flow_generator=flow_generator,
        )

    def _create_use_case_create_intersection_events(
        self,
        section_repository: SectionRepository,
        get_all_tracks: GetAllTracks,
        add_events: AddEvents,
    ) -> CreateIntersectionEvents:
        intersect = self._create_intersect(get_all_tracks)
        return SimpleCreateIntersectionEvents(intersect, section_repository, add_events)

    def _create_intersect(self, get_all_tracks: GetAllTracks) -> RunIntersect:
        return SimpleRunIntersect(
            intersect_implementation=ShapelyIntersector(ShapelyMapper()),
            intersect_parallelizer=MultiprocessingIntersectParallelization(),
            get_all_tracks=get_all_tracks,
        )

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

    def _create_export_counts(
        self,
        event_repository: EventRepository,
        flow_repository: FlowRepository,
        track_repository: TrackRepository,
    ) -> ExportCounts:
        return ExportTrafficCounting(
            event_repository,
            flow_repository,
            FilterBySectionEnterEvent(SimpleRoadUserAssigner()),
            SimpleTaggerFactory(track_repository),
            FillZerosExporterFactory(SimpleExporterFactory()),
        )

    def _create_use_case_create_events(
        self,
        section_repository: SectionRepository,
        clear_events: ClearAllEvents,
        get_all_tracks: GetAllTracks,
        add_events: AddEvents,
    ) -> CreateEvents:
        run_intersect = self._create_intersect(get_all_tracks)
        create_intersection_events = SimpleCreateIntersectionEvents(
            run_intersect, section_repository, add_events
        )
        scene_action_detector = SceneActionDetector(SceneEventBuilder())
        create_scene_events = SimpleCreateSceneEvents(
            get_all_tracks, scene_action_detector, add_events
        )
        return CreateEvents(
            clear_events, create_intersection_events, create_scene_events
        )

    def _create_tracks_intersecting_sections(
        self,
        get_all_tracks: GetAllTracks,
        intersect_implementation: IntersectImplementation,
    ) -> TracksIntersectingSections:
        return SimpleTracksIntersectingSections(
            get_all_tracks, intersect_implementation
        )

    @staticmethod
    def _create_use_case_load_otflow(
        clear_all_sections: ClearAllSections,
        clear_all_flows: ClearAllFlows,
        clear_all_events: ClearAllEvents,
        flow_parser: FlowParser,
        add_section: AddSection,
        add_flow: AddFlow,
    ) -> LoadOtflow:
        return LoadOtflow(
            clear_all_sections,
            clear_all_flows,
            clear_all_events,
            flow_parser,
            add_section,
            add_flow,
        )

    @staticmethod
    def _create_use_case_clear_all_repositories(
        clear_all_events: ClearAllEvents,
        clear_all_flows: ClearAllFlows,
        clear_all_sections: ClearAllSections,
        clear_all_track_to_videos: ClearAllTrackToVideos,
        clear_all_tracks: ClearAllTracks,
        clear_all_videos: ClearAllVideos,
    ) -> ClearRepositories:
        return ClearRepositories(
            clear_all_events,
            clear_all_flows,
            clear_all_sections,
            clear_all_track_to_videos,
            clear_all_tracks,
            clear_all_videos,
        )

    @staticmethod
    def _create_use_case_start_new_project(
        clear_repositories: ClearRepositories,
        reset_project_config: ResetProjectConfig,
        track_view_state: TrackViewState,
    ) -> StartNewProject:
        return StartNewProject(
            clear_repositories, reset_project_config, track_view_state
        )

    @staticmethod
    def _create_reset_project_config(
        project_updater: ProjectUpdater,
    ) -> ResetProjectConfig:
        return ResetProjectConfig(project_updater)

    @staticmethod
    def _create_project_updater(datastore: Datastore) -> ProjectUpdater:
        return ProjectUpdater(datastore)

    def _create_track_file_repository(self) -> TrackFileRepository:
        return TrackFileRepository()
