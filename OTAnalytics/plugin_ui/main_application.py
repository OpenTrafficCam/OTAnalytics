import logging
from typing import Optional, Sequence

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
from OTAnalytics.application.config import DEFAULT_NUM_PROCESSES
from OTAnalytics.application.datastore import (
    Datastore,
    EventListParser,
    FlowParser,
    TrackParser,
    TrackToVideoRepository,
    VideoParser,
)
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.logger import logger, setup_logger
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
from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.create_events import (
    CreateEvents,
    CreateIntersectionEvents,
    SimpleCreateIntersectionEvents,
    SimpleCreateSceneEvents,
)
from OTAnalytics.application.use_cases.cut_tracks_with_sections import (
    CutTracksIntersectingSection,
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
    TracksAssignedToSelectedFlows,
    TracksIntersectingSelectedSections,
    TracksNotIntersectingSelection,
    TracksOverlapOccurrenceWindow,
)
from OTAnalytics.application.use_cases.load_otflow import LoadOtflow
from OTAnalytics.application.use_cases.load_track_files import LoadTrackFiles
from OTAnalytics.application.use_cases.reset_project_config import ResetProjectConfig
from OTAnalytics.application.use_cases.section_repository import (
    AddSection,
    ClearAllSections,
    GetAllSections,
    GetSectionsById,
    RemoveSection,
)
from OTAnalytics.application.use_cases.start_new_project import StartNewProject
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    ClearAllTracks,
    GetAllTrackFiles,
    GetAllTrackIds,
    GetTracksFromIds,
    GetTracksWithoutSingleDetections,
    RemoveTracks,
)
from OTAnalytics.application.use_cases.track_to_video_repository import (
    ClearAllTrackToVideos,
)
from OTAnalytics.application.use_cases.update_project import ProjectUpdater
from OTAnalytics.application.use_cases.video_repository import ClearAllVideos
from OTAnalytics.domain.event import EventRepository, SceneEventBuilder
from OTAnalytics.domain.filter import FilterElementSettingRestorer
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.intersect import IntersectImplementation
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.section import SectionRepository
from OTAnalytics.domain.track import (
    ByMaxConfidence,
    PythonTrackDataset,
    TrackFileRepository,
    TrackIdProvider,
    TrackRepository,
)
from OTAnalytics.domain.video import VideoRepository
from OTAnalytics.plugin_filter.dataframe_filter import DataFrameFilterBuilder
from OTAnalytics.plugin_intersect.shapely.intersect import ShapelyIntersector
from OTAnalytics.plugin_intersect.shapely.mapping import ShapelyMapper
from OTAnalytics.plugin_intersect.simple.cut_tracks_with_sections import (
    SimpleCutTrackSegmentBuilder,
    SimpleCutTracksIntersectingSection,
    SimpleCutTracksWithSection,
)
from OTAnalytics.plugin_intersect.simple_intersect import (
    SimpleRunIntersect,
    SimpleTracksIntersectingSections,
)
from OTAnalytics.plugin_intersect_parallelization.multiprocessing import (
    MultiprocessingIntersectParallelization,
)
from OTAnalytics.plugin_parser.export import (
    AddSectionInformationExporterFactory,
    FillZerosExporterFactory,
    SimpleExporterFactory,
)
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    CachedVideoParser,
    OtConfigParser,
    OtEventListParser,
    OtFlowParser,
    OttrkParser,
    OttrkVideoParser,
    PythonDetectionParser,
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
    MatplotlibTrackPlotter,
    PandasDataFrameProvider,
    PandasTrackProvider,
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
from OTAnalytics.plugin_video_processing.video_reader import OpenCvVideoReader


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
        video_parser = self._create_video_parser()
        video_repository = self._create_video_repository()
        track_to_video_repository = self._create_track_to_video_repository()
        datastore = self._create_datastore(
            video_parser,
            video_repository,
            track_repository,
            track_file_repository,
            track_to_video_repository,
            section_repository,
            flow_repository,
            event_repository,
            pulling_progressbar_builder,
        )
        track_state = self._create_track_state()
        track_view_state = self._create_track_view_state()
        section_state = self._create_section_state(section_repository)
        flow_state = self._create_flow_state()
        road_user_assigner = FilterBySectionEnterEvent(SimpleRoadUserAssigner())
        cached_pandas_track_provider = self._create_pandas_track_provider(
            datastore, track_view_state, pulling_progressbar_builder
        )
        pandas_data_provider = self._wrap_pandas_track_offset_provider(
            cached_pandas_track_provider, track_view_state
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
        get_tracks_without_single_detections = GetTracksWithoutSingleDetections(
            track_repository
        )
        get_tracks_from_ids = GetTracksFromIds(track_repository)
        add_all_tracks = AddAllTracks(track_repository)
        remove_tracks = RemoveTracks(track_repository)
        clear_all_tracks = ClearAllTracks(track_repository)

        get_sections_bv_id = GetSectionsById(section_repository)
        add_section = AddSection(section_repository)
        remove_section = RemoveSection(section_repository)
        clear_all_sections = ClearAllSections(section_repository)

        generate_flows = self._create_flow_generator(
            section_repository, flow_repository
        )
        add_flow = AddFlow(flow_repository)
        clear_all_flows = ClearAllFlows(flow_repository)

        add_events = AddEvents(event_repository)
        clear_all_events = ClearAllEvents(event_repository)

        clear_all_videos = ClearAllVideos(datastore._video_repository)
        clear_all_track_to_videos = ClearAllTrackToVideos(
            datastore._track_to_video_repository
        )

        create_events = self._create_use_case_create_events(
            section_repository,
            clear_all_events,
            get_tracks_without_single_detections,
            add_events,
            DEFAULT_NUM_PROCESSES,
        )
        intersect_tracks_with_sections = (
            self._create_use_case_create_intersection_events(
                section_repository,
                get_tracks_without_single_detections,
                add_events,
                DEFAULT_NUM_PROCESSES,
            )
        )
        export_counts = self._create_export_counts(
            event_repository,
            flow_repository,
            track_repository,
            get_sections_bv_id,
            create_events,
        )
        load_otflow = self._create_use_case_load_otflow(
            clear_all_sections,
            clear_all_flows,
            clear_all_events,
            datastore._flow_parser,
            add_section,
            add_flow,
        )
        load_track_files = self._create_load_tracks_file(
            video_parser,
            track_repository,
            track_file_repository,
            video_repository,
            track_to_video_repository,
            pulling_progressbar_builder,
            tracks_metadata,
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
        tracks_intersecting_sections = self._create_tracks_intersecting_sections(
            GetTracksWithoutSingleDetections(track_repository),
            ShapelyIntersector(),
        )
        cut_tracks_intersecting_section = self._create_cut_tracks_intersecting_section(
            get_sections_bv_id,
            get_tracks_without_single_detections,
            get_tracks_from_ids,
            tracks_intersecting_sections,
            add_all_tracks,
            remove_tracks,
            remove_section,
            track_view_state,
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
            load_track_files,
        )
        section_repository.register_sections_observer(cut_tracks_intersecting_section)
        section_repository.register_section_changed_observer(
            cut_tracks_intersecting_section.notify_section_changed
        )
        cut_tracks_intersecting_section.register(clear_all_events.on_tracks_cut)
        application.connect_clear_event_repository_observer()
        flow_parser: FlowParser = application._datastore._flow_parser
        name_generator = ArrowFlowNameGenerator()
        dummy_viewmodel = DummyViewModel(
            application,
            flow_parser,
            name_generator,
            event_list_export_formats=AVAILABLE_EVENTLIST_EXPORTERS,
        )
        application.register_video_observer(dummy_viewmodel)
        application.register_sections_observer(dummy_viewmodel)
        application.register_flows_observer(dummy_viewmodel)
        application.register_flow_changed_observer(dummy_viewmodel._on_flow_changed)
        application.track_view_state.selected_videos.register(
            dummy_viewmodel._update_selected_videos
        )
        application.section_state.selected_sections.register(
            dummy_viewmodel._update_selected_sections
        )
        application.flow_state.selected_flows.register(
            dummy_viewmodel._update_selected_flows
        )
        application.track_view_state.background_image.register(
            dummy_viewmodel._on_background_updated
        )
        application.track_view_state.track_offset.register(
            dummy_viewmodel._update_offset
        )
        application.track_view_state.filter_element.register(
            dummy_viewmodel._update_date_range
        )
        application.action_state.action_running.register(
            dummy_viewmodel._notify_action_running_state
        )
        # TODO: Refactor observers - move registering to subjects happening in
        #   constructor dummy_viewmodel
        # cut_tracks_intersecting_section.register(
        #    cached_pandas_track_provider.on_tracks_cut
        # )
        cut_tracks_intersecting_section.register(dummy_viewmodel.on_tracks_cut)
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
        event_repository.register_observer(image_updater.notify_events)

        for layer in layers:
            layer.register(image_updater.notify_layers)
        main_window = ModifiedCTk(dummy_viewmodel)
        pulling_progressbar_popup_builder.add_widget(main_window)
        OTAnalyticsGui(main_window, dummy_viewmodel, layers).start()

    def start_cli(self, cli_args: CliArguments) -> None:
        track_repository = self._create_track_repository()
        section_repository = self._create_section_repository()
        flow_repository = self._create_flow_repository()
        track_parser = self._create_track_parser(track_repository)
        flow_parser = self._create_flow_parser()
        event_repository = self._create_event_repository()
        add_section = AddSection(section_repository)
        get_sections_by_id = GetSectionsById(section_repository)
        add_flow = AddFlow(flow_repository)
        add_events = AddEvents(event_repository)
        get_tracks_without_single_detections = GetTracksWithoutSingleDetections(
            track_repository
        )
        get_all_track_ids = GetAllTrackIds(track_repository)
        clear_all_events = ClearAllEvents(event_repository)
        create_events = self._create_use_case_create_events(
            section_repository,
            clear_all_events,
            get_tracks_without_single_detections,
            add_events,
            cli_args.num_processes,
        )
        tracks_intersecting_sections = self._create_tracks_intersecting_sections(
            GetTracksWithoutSingleDetections(track_repository),
            ShapelyIntersector(),
        )
        cut_tracks = self._create_cut_tracks_intersecting_section(
            GetSectionsById(section_repository),
            get_tracks_without_single_detections,
            GetTracksFromIds(track_repository),
            tracks_intersecting_sections,
            AddAllTracks(track_repository),
            RemoveTracks(track_repository),
            RemoveSection(section_repository),
            TrackViewState(),
        )
        add_all_tracks = AddAllTracks(track_repository)
        clear_all_tracks = ClearAllTracks(track_repository)
        export_counts = self._create_export_counts(
            event_repository,
            flow_repository,
            track_repository,
            get_sections_by_id,
            create_events,
        )
        OTAnalyticsCli(
            cli_args,
            track_parser=track_parser,
            flow_parser=flow_parser,
            event_repository=event_repository,
            get_all_sections=GetAllSections(section_repository),
            add_section=add_section,
            create_events=create_events,
            export_counts=export_counts,
            cut_tracks=cut_tracks,
            add_all_tracks=add_all_tracks,
            get_all_track_ids=get_all_track_ids,
            add_flow=add_flow,
            clear_all_tracks=clear_all_tracks,
            tracks_metadata=TracksMetadata(track_repository),
            progressbar=TqdmBuilder(),
        ).start()

    def _create_datastore(
        self,
        video_parser: VideoParser,
        video_repository: VideoRepository,
        track_repository: TrackRepository,
        track_file_repository: TrackFileRepository,
        track_to_video_repository: TrackToVideoRepository,
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
        track_parser = self._create_track_parser(track_repository)
        flow_parser = self._create_flow_parser()
        event_list_parser = self._create_event_list_parser()
        track_video_parser = OttrkVideoParser(video_parser)
        config_parser = OtConfigParser(
            video_parser=video_parser,
            flow_parser=flow_parser,
        )
        return Datastore(
            track_repository,
            track_file_repository,
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
        # return TrackRepository(PandasTrackDataset.from_list([]))
        return TrackRepository(PythonTrackDataset())

    def _create_track_parser(self, track_repository: TrackRepository) -> TrackParser:
        # calculator = PandasByMaxConfidence()
        # detection_parser = PandasDetectionParser(
        #     calculator, track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT
        # )
        calculator = ByMaxConfidence()
        detection_parser = PythonDetectionParser(
            calculator, track_repository, track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT
        )
        return OttrkParser(detection_parser)

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

    def _create_pandas_track_provider(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
        progressbar: ProgressbarBuilder,
    ) -> PandasTrackProvider:
        dataframe_filter_builder = self._create_dataframe_filter_builder()
        # return PandasTrackProvider(
        #     datastore, track_view_state, dataframe_filter_builder, progressbar
        # )
        return CachedPandasTrackProvider(
            datastore, track_view_state, dataframe_filter_builder, progressbar
        )

    @staticmethod
    def _wrap_pandas_track_offset_provider(
        other: PandasDataFrameProvider,
        track_view_state: TrackViewState,
    ) -> PandasDataFrameProvider:
        return PandasTracksOffsetProvider(other, track_view_state)

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

    def _create_track_start_end_point_plotter(
        self,
        state: TrackViewState,
        pandas_data_provider: PandasDataFrameProvider,
        track_repository: TrackRepository,
        color_palette_provider: ColorPaletteProvider,
        enable_legend: bool,
        id_filter: Optional[TrackIdProvider] = None,
    ) -> Plotter:
        data_provider = pandas_data_provider
        data_provider = FilterById(
            pandas_data_provider,
            id_filter=TracksOverlapOccurrenceWindow(
                other=id_filter,
                track_repository=track_repository,
                track_view_state=state,
            ),
        )
        track_plotter = MatplotlibTrackPlotter(
            TrackStartEndPointPlotter(
                data_provider,
                color_palette_provider,
                enable_legend=enable_legend,
            ),
        )
        return PlotterPrototype(state, track_plotter)

    def _create_track_highlight_geometry_plotter(
        self,
        state: TrackViewState,
        tracks_intersecting_selected_sections: TracksIntersectingSelectedSections,
        pandas_track_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
        enable_legend: bool,
    ) -> Plotter:
        filter_by_id = FilterById(
            pandas_track_provider, id_filter=tracks_intersecting_selected_sections
        )
        return self._create_track_geometry_plotter(
            state,
            filter_by_id,
            color_palette_provider,
            alpha=1,
            enable_legend=enable_legend,
        )

    def _create_tracks_intersecting_selected_sections(
        self,
        section_state: SectionState,
        tracks_intersecting_sections: TracksIntersectingSections,
        get_sections_by_id: GetSectionsById,
    ) -> TracksIntersectingSelectedSections:
        return TracksIntersectingSelectedSections(
            section_state, tracks_intersecting_sections, get_sections_by_id
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

    def _create_start_end_point_tracks_intersecting_sections_plotter(
        self,
        state: TrackViewState,
        tracks_intersecting_sections: TracksIntersectingSelectedSections,
        pandas_track_provider: PandasDataFrameProvider,
        track_repository: TrackRepository,
        color_palette_provider: ColorPaletteProvider,
        enable_legend: bool,
    ) -> Plotter:
        return self._create_track_start_end_point_plotter(
            state,
            pandas_track_provider,
            track_repository,
            color_palette_provider,
            enable_legend=enable_legend,
            id_filter=tracks_intersecting_sections,
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
            pandas_track_provider,
            track_repository,
            color_palette_provider,
            enable_legend=enable_legend,
            id_filter=tracks_not_intersecting_sections,
        )

    def _create_highlight_tracks_assigned_to_flow(
        self,
        state: TrackViewState,
        pandas_track_provider: PandasDataFrameProvider,
        color_palette_provider: ColorPaletteProvider,
        tracks_assigned_to_flow: TracksAssignedToSelectedFlows,
        enable_legend: bool,
    ) -> Plotter:
        filter_by_id = FilterById(
            pandas_track_provider, id_filter=tracks_assigned_to_flow
        )
        return self._create_track_geometry_plotter(
            state,
            filter_by_id,
            color_palette_provider,
            alpha=1,
            enable_legend=enable_legend,
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
            alpha=0.5,
            enable_legend=True,
        )
        tracks_intersecting_sections = self._create_tracks_intersecting_sections(
            GetTracksWithoutSingleDetections(datastore._track_repository),
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

        highlight_tracks_intersecting_sections = (
            self._create_track_highlight_geometry_plotter(
                track_view_state,
                tracks_intersecting_selected_sections,
                data_provider_all_filters,
                color_palette_provider,
                enable_legend=False,
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
        start_end_points_tracks_intersecting_sections = (
            self._create_start_end_point_tracks_intersecting_sections_plotter(
                track_view_state,
                tracks_intersecting_selected_sections,
                data_provider_class_filter,
                datastore._track_repository,
                color_palette_provider,
                enable_legend=False,
            )
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
            data_provider_class_filter,
            datastore._track_repository,
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
                track_view_state,
                data_provider_all_filters,
                color_palette_provider,
                tracks_assigned_to_flow,
                enable_legend=False,
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
            "Show all tracks", track_geometry_plotter, enabled=False
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

    @staticmethod
    def _create_section_state(section_repository: SectionRepository) -> SectionState:
        return SectionState(GetSectionsById(section_repository))

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
        get_tracks: GetTracksWithoutSingleDetections,
        add_events: AddEvents,
        num_processes: int,
    ) -> CreateIntersectionEvents:
        intersect = self._create_intersect(get_tracks, num_processes)
        return SimpleCreateIntersectionEvents(intersect, section_repository, add_events)

    @staticmethod
    def _create_intersect(
        get_tracks: GetTracksWithoutSingleDetections, num_processes: int
    ) -> RunIntersect:
        return SimpleRunIntersect(
            intersect_implementation=ShapelyIntersector(ShapelyMapper()),
            intersect_parallelizer=MultiprocessingIntersectParallelization(
                num_processes
            ),
            get_tracks=get_tracks,
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

    @staticmethod
    def _create_export_counts(
        event_repository: EventRepository,
        flow_repository: FlowRepository,
        track_repository: TrackRepository,
        get_sections_by_id: GetSectionsById,
        create_events: CreateEvents,
    ) -> ExportCounts:
        return ExportTrafficCounting(
            event_repository,
            flow_repository,
            get_sections_by_id,
            create_events,
            FilterBySectionEnterEvent(SimpleRoadUserAssigner()),
            SimpleTaggerFactory(track_repository),
            FillZerosExporterFactory(
                AddSectionInformationExporterFactory(SimpleExporterFactory())
            ),
        )

    def _create_use_case_create_events(
        self,
        section_repository: SectionRepository,
        clear_events: ClearAllEvents,
        get_tracks: GetTracksWithoutSingleDetections,
        add_events: AddEvents,
        num_processes: int,
    ) -> CreateEvents:
        run_intersect = self._create_intersect(get_tracks, num_processes)
        create_intersection_events = SimpleCreateIntersectionEvents(
            run_intersect, section_repository, add_events
        )
        scene_action_detector = SceneActionDetector(SceneEventBuilder())
        create_scene_events = SimpleCreateSceneEvents(
            get_tracks, scene_action_detector, add_events
        )
        return CreateEvents(
            clear_events, create_intersection_events, create_scene_events
        )

    @staticmethod
    def _create_tracks_intersecting_sections(
        get_tracks: GetTracksWithoutSingleDetections,
        intersect_implementation: IntersectImplementation,
    ) -> TracksIntersectingSections:
        return SimpleTracksIntersectingSections(get_tracks, intersect_implementation)

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

    @staticmethod
    def _create_cut_tracks_intersecting_section(
        get_sections_by_id: GetSectionsById,
        get_tracks: GetTracksWithoutSingleDetections,
        get_tracks_from_ids: GetTracksFromIds,
        tracks_intersecting_sections: TracksIntersectingSections,
        add_all_tracks: AddAllTracks,
        remove_tracks: RemoveTracks,
        remove_section: RemoveSection,
        track_view_state: TrackViewState,
    ) -> CutTracksIntersectingSection:
        track_builder = SimpleCutTrackSegmentBuilder(ByMaxConfidence())
        cut_tracks_with_section = SimpleCutTracksWithSection(
            get_tracks_from_ids, ShapelyMapper(), track_builder, track_view_state
        )
        return SimpleCutTracksIntersectingSection(
            get_sections_by_id,
            get_tracks,
            tracks_intersecting_sections,
            cut_tracks_with_section,
            add_all_tracks,
            remove_tracks,
            remove_section,
        )

    def _create_load_tracks_file(
        self,
        video_parser: VideoParser,
        track_repository: TrackRepository,
        track_file_repository: TrackFileRepository,
        video_repository: VideoRepository,
        track_to_video_repository: TrackToVideoRepository,
        progressbar: ProgressbarBuilder,
        tracks_metadata: TracksMetadata,
    ) -> LoadTrackFiles:
        track_parser = self._create_track_parser(track_repository)
        track_video_parser = OttrkVideoParser(video_parser)
        return LoadTrackFiles(
            track_parser,
            track_video_parser,
            track_repository,
            track_file_repository,
            video_repository,
            track_to_video_repository,
            progressbar,
            tracks_metadata,
        )

    def _create_video_parser(self) -> VideoParser:
        return CachedVideoParser(SimpleVideoParser(OpenCvVideoReader()))

    def _create_video_repository(self) -> VideoRepository:
        return VideoRepository()

    def _create_track_to_video_repository(self) -> TrackToVideoRepository:
        return TrackToVideoRepository()
