import logging
from functools import cached_property
from pathlib import Path
from typing import Sequence

from OTAnalytics.adapter_ui.abstract_progressbar_popup import ProgressbarPopupBuilder
from OTAnalytics.adapter_visualization.color_provider import (
    DEFAULT_COLOR_PALETTE,
    ColorPaletteProvider,
)
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
from OTAnalytics.application.config_specification import OtConfigDefaultValueProvider
from OTAnalytics.application.datastore import (
    Datastore,
    EventListParser,
    TrackParser,
    TrackToVideoRepository,
    VideoParser,
)
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.logger import logger, setup_logger
from OTAnalytics.application.parser.cli_parser import (
    CliParseError,
    CliParser,
    CliValueProvider,
)
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.plotting import LayeredPlotter, LayerGroup, PlottingLayer
from OTAnalytics.application.run_configuration import RunConfiguration
from OTAnalytics.application.state import (
    ActionState,
    FileState,
    FlowState,
    SectionState,
    SelectedVideoUpdate,
    TrackImageUpdater,
    TrackPropertiesUpdater,
    TracksMetadata,
    TrackState,
    TrackViewState,
    VideosMetadata,
)
from OTAnalytics.application.ui.frame_control import (
    SwitchToEvent,
    SwitchToNext,
    SwitchToPrevious,
)
from OTAnalytics.application.use_cases.add_new_remark import AddNewRemark
from OTAnalytics.application.use_cases.apply_cli_cuts import ApplyCliCuts
from OTAnalytics.application.use_cases.clear_repositories import ClearRepositories
from OTAnalytics.application.use_cases.config import SaveOtconfig
from OTAnalytics.application.use_cases.config_has_changed import (
    ConfigHasChanged,
    OtconfigHasChanged,
    OtflowHasChanged,
)
from OTAnalytics.application.use_cases.create_events import (
    CreateEvents,
    CreateIntersectionEvents,
    FilterOutCuttingSections,
    MissingEventsSectionProvider,
    SectionProvider,
    SimpleCreateIntersectionEvents,
    SimpleCreateSceneEvents,
)
from OTAnalytics.application.use_cases.create_intersection_events import (
    BatchedTracksRunIntersect,
)
from OTAnalytics.application.use_cases.cut_tracks_with_sections import (
    CutTracksIntersectingSection,
)
from OTAnalytics.application.use_cases.event_repository import (
    AddEvents,
    ClearAllEvents,
    GetAllEnterSectionEvents,
)
from OTAnalytics.application.use_cases.filter_visualization import (
    CreateDefaultFilterRange,
    EnableFilterTrackByDate,
)
from OTAnalytics.application.use_cases.flow_repository import (
    AddAllFlows,
    AddFlow,
    ClearAllFlows,
    GetAllFlows,
)
from OTAnalytics.application.use_cases.flow_statistics import (
    NumberOfTracksAssignedToEachFlow,
)
from OTAnalytics.application.use_cases.generate_flows import (
    ArrowFlowNameGenerator,
    CrossProductFlowGenerator,
    FilterExisting,
    FilterSameSection,
    FlowIdGenerator,
    GenerateFlows,
    RepositoryFlowIdGenerator,
)
from OTAnalytics.application.use_cases.get_current_project import GetCurrentProject
from OTAnalytics.application.use_cases.get_current_remark import GetCurrentRemark
from OTAnalytics.application.use_cases.get_road_user_assignments import (
    GetRoadUserAssignments,
)
from OTAnalytics.application.use_cases.highlight_intersections import (
    IntersectionRepository,
    TracksAssignedToAllFlows,
    TracksIntersectingAllNonCuttingSections,
)
from OTAnalytics.application.use_cases.inside_cutting_section import (
    TrackIdsInsideCuttingSections,
)
from OTAnalytics.application.use_cases.intersection_repository import (
    ClearAllIntersections,
)
from OTAnalytics.application.use_cases.load_otconfig import LoadOtconfig
from OTAnalytics.application.use_cases.load_otflow import LoadOtflow
from OTAnalytics.application.use_cases.load_track_files import LoadTrackFiles
from OTAnalytics.application.use_cases.preload_input_files import PreloadInputFiles
from OTAnalytics.application.use_cases.quick_save_configuration import (
    QuickSaveConfiguration,
)
from OTAnalytics.application.use_cases.reset_project_config import ResetProjectConfig
from OTAnalytics.application.use_cases.road_user_assignment_export import (
    ExportRoadUserAssignments,
)
from OTAnalytics.application.use_cases.save_otflow import SaveOtflow
from OTAnalytics.application.use_cases.section_repository import (
    AddAllSections,
    AddSection,
    ClearAllSections,
    GetAllSections,
    GetCuttingSections,
    GetSectionsById,
    RemoveSection,
)
from OTAnalytics.application.use_cases.start_new_project import StartNewProject
from OTAnalytics.application.use_cases.suggest_save_path import SavePathSuggester
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    ClearAllTracks,
    GetAllTrackFiles,
    GetAllTrackIds,
    GetAllTracks,
    GetTracksWithoutSingleDetections,
    RemoveTracks,
    TrackRepositorySize,
)
from OTAnalytics.application.use_cases.track_statistics import CalculateTrackStatistics
from OTAnalytics.application.use_cases.track_statistics_export import (
    ExportTrackStatistics,
)
from OTAnalytics.application.use_cases.track_to_video_repository import (
    ClearAllTrackToVideos,
)
from OTAnalytics.application.use_cases.update_project import ProjectUpdater
from OTAnalytics.application.use_cases.video_repository import (
    AddAllVideos,
    ClearAllVideos,
    GetAllVideos,
)
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.filter import FilterElementSettingRestorer
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.remark import RemarkRepository
from OTAnalytics.domain.section import SectionRepository
from OTAnalytics.domain.track_repository import TrackFileRepository, TrackRepository
from OTAnalytics.domain.video import VideoRepository
from OTAnalytics.helpers.time_profiling import log_processing_time
from OTAnalytics.plugin_datastore.python_track_store import ByMaxConfidence
from OTAnalytics.plugin_datastore.track_geometry_store.pygeos_store import (
    PygeosTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    FilteredPandasTrackDataset,
    PandasByMaxConfidence,
    PandasTrackDataset,
)
from OTAnalytics.plugin_intersect.simple.cut_tracks_with_sections import (
    SimpleCutTracksIntersectingSection,
)
from OTAnalytics.plugin_intersect.simple_intersect import (
    SimpleTracksIntersectingSections,
)
from OTAnalytics.plugin_intersect_parallelization.multiprocessing import (
    MultiprocessingIntersectParallelization,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.calculation_strategy import (
    DetectionRateByPercentile,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.metric_rates_builder import (
    MetricRatesBuilder,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.svz.metric_rates import (
    SVZ_CLASSIFICATION,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.svz.number_of_tracks_to_be_validated import (  # noqa
    SvzNumberOfTracksToBeValidated,
)
from OTAnalytics.plugin_number_of_tracks_to_be_validated.tracks_as_dataframe_provider import (  # noqa
    TracksAsDataFrameProvider,
)
from OTAnalytics.plugin_parser.argparse_cli_parser import ArgparseCliParser
from OTAnalytics.plugin_parser.export import (
    AddSectionInformationExporterFactory,
    CachedExporterFactory,
    FillZerosExporterFactory,
    SimpleExporterFactory,
)
from OTAnalytics.plugin_parser.json_parser import parse_json
from OTAnalytics.plugin_parser.otconfig_parser import (
    FixMissingAnalysis,
    MultiFixer,
    OtConfigFormatFixer,
    OtConfigParser,
)
from OTAnalytics.plugin_parser.otvision_parser import (
    DEFAULT_TRACK_LENGTH_LIMIT,
    CachedVideoParser,
    OtEventListParser,
    OtFlowParser,
    OttrkFormatFixer,
    OttrkParser,
    OttrkVideoParser,
    SimpleVideoParser,
)
from OTAnalytics.plugin_parser.pandas_parser import PandasDetectionParser
from OTAnalytics.plugin_parser.road_user_assignment_export import (
    SimpleRoadUserAssignmentExporterFactory,
)
from OTAnalytics.plugin_parser.streaming_parser import (
    PythonStreamDetectionParser,
    StreamOttrkParser,
    StreamTrackParser,
)
from OTAnalytics.plugin_parser.track_export import CsvTrackExport
from OTAnalytics.plugin_parser.track_statistics_export import (
    CachedTrackStatisticsExporterFactory,
    SimpleTrackStatisticsExporterFactory,
)
from OTAnalytics.plugin_progress.tqdm_progressbar import TqdmBuilder
from OTAnalytics.plugin_prototypes.eventlist_exporter.eventlist_exporter import (
    AVAILABLE_EVENTLIST_EXPORTERS,
    provide_available_eventlist_exporter,
)
from OTAnalytics.plugin_ui.cli import (
    OTAnalyticsBulkCli,
    OTAnalyticsCli,
    OTAnalyticsStreamCli,
)
from OTAnalytics.plugin_ui.intersection_repository import PythonIntersectionRepository
from OTAnalytics.plugin_ui.visualization.visualization import VisualizationBuilder
from OTAnalytics.plugin_video_processing.video_reader import PyAvVideoReader

DETECTION_RATE_PERCENTILE_VALUE = 0.9


class ApplicationStarter:
    @log_processing_time(description="overall")
    def start(self) -> None:
        self._setup_logger(
            Path(self.run_config.log_file),
            self.run_config.logfile_overwrite,
            self.run_config.debug,
        )
        if self.run_config.start_cli:
            try:

                self.start_cli()
                # add command line tag for activating -> add to PipelineBenchmark,
                # add github actions for benchmark
                # regression test lokal runner neben benchmark ->
                # OTC -> test data -> 6-1145, flow in 00 -> in test resource ordner

            except CliParseError as e:
                logger().exception(e, exc_info=True)
        else:
            self.start_gui()

    @cached_property
    def run_config(self) -> RunConfiguration:
        cli_args_parser = self._build_cli_argument_parser()
        cli_args = cli_args_parser.parse()
        cli_value_provider: OtConfigDefaultValueProvider = CliValueProvider(cli_args)
        format_fixer = self._create_format_fixer(cli_value_provider)
        config_parser = OtConfigParser(
            format_fixer=format_fixer,
            video_parser=self.video_parser,
            flow_parser=self.flow_parser,
        )

        if config_file := cli_args.config_file:
            config = config_parser.parse(Path(config_file))
            return RunConfiguration(self.flow_parser, cli_args, config)
        return RunConfiguration(self.flow_parser, cli_args, None)

    @staticmethod
    def _create_format_fixer(
        default_value_provider: OtConfigDefaultValueProvider,
    ) -> OtConfigFormatFixer:
        return MultiFixer([FixMissingAnalysis(default_value_provider)])

    def _build_cli_argument_parser(self) -> CliParser:
        return ArgparseCliParser()

    def _setup_logger(self, log_file: Path, overwrite: bool, debug: bool) -> None:
        if debug:
            setup_logger(
                log_file=log_file, overwrite=overwrite, log_level=logging.DEBUG
            )
        else:
            setup_logger(log_file=log_file, overwrite=overwrite, log_level=logging.INFO)

    def start_gui(self) -> None:
        from OTAnalytics.plugin_ui.customtkinter_gui.dummy_viewmodel import (
            DummyViewModel,
        )
        from OTAnalytics.plugin_ui.customtkinter_gui.gui import (
            ModifiedCTk,
            OTAnalyticsGui,
        )

        self.track_repository.register_tracks_observer(self.clear_all_intersections)
        self.section_repository.register_sections_observer(self.clear_all_intersections)
        self.section_repository.register_section_changed_observer(
            self.clear_all_intersections.on_section_changed
        )
        layer_groups, layers = self._create_layers()
        plotter = LayeredPlotter(layers=layers)
        track_image_updater = self._create_track_image_updater(plotter)
        self.track_view_state.selected_videos.register(
            self.track_properties_updater.notify_videos
        )
        self.track_view_state.selected_videos.register(track_image_updater.notify_video)

        tracks_metadata = self._create_tracks_metadata()
        # TODO: Should not register to tracks_metadata._classifications but to
        # TODO: ottrk metadata detection classes
        tracks_metadata._classifications.register(
            observer=self.color_palette_provider.update
        )
        action_state = self._create_action_state()
        filter_element_settings_restorer = (
            self._create_filter_element_setting_restorer()
        )

        get_all_track_files = self._create_get_all_track_files()
        get_all_tracks = GetAllTracks(self.track_repository)
        get_tracks_without_single_detections = GetTracksWithoutSingleDetections(
            self.track_repository
        )
        add_all_tracks = AddAllTracks(self.track_repository)
        remove_tracks = RemoveTracks(self.track_repository)
        clear_all_tracks = ClearAllTracks(self.track_repository)

        get_sections = GetAllSections(self.section_repository)
        get_sections_by_id = GetSectionsById(self.section_repository)
        add_section = AddSection(self.section_repository)
        remove_section = RemoveSection(self.section_repository)
        clear_all_sections = ClearAllSections(self.section_repository)
        generate_flows = self._create_flow_generator(
            FilterOutCuttingSections(get_sections)
        )
        add_flow = AddFlow(self.flow_repository)
        clear_all_flows = ClearAllFlows(self.flow_repository)

        add_events = AddEvents(self.event_repository)
        clear_all_events = ClearAllEvents(self.event_repository)

        clear_all_videos = ClearAllVideos(self.video_repository)
        clear_all_track_to_videos = ClearAllTrackToVideos(
            self.track_to_video_repository
        )
        section_provider = FilterOutCuttingSections(
            MissingEventsSectionProvider(self.section_repository, self.event_repository)
        )
        create_events = self._create_use_case_create_events(
            section_provider,
            clear_all_events,
            get_all_tracks,
            get_tracks_without_single_detections,
            add_events,
            DEFAULT_NUM_PROCESSES,
        )
        intersect_tracks_with_sections = (
            self._create_use_case_create_intersection_events(
                section_provider,
                get_all_tracks,
                add_events,
                DEFAULT_NUM_PROCESSES,
            )
        )
        export_counts = self._create_export_counts(get_sections_by_id, create_events)
        load_otflow = self._create_use_case_load_otflow(
            clear_all_sections, clear_all_flows, clear_all_events, add_section, add_flow
        )
        load_track_files = self._create_load_tracks_file(tracks_metadata)
        clear_repositories = self._create_use_case_clear_all_repositories(
            clear_all_events,
            clear_all_flows,
            clear_all_sections,
            clear_all_track_to_videos,
            clear_all_tracks,
            clear_all_videos,
        )
        project_updater = self._create_project_updater()
        reset_project_config = self._create_reset_project_config(project_updater)
        start_new_project = self._create_use_case_start_new_project(
            clear_repositories, reset_project_config
        )
        cut_tracks_intersecting_section = self._create_cut_tracks_intersecting_section(
            get_sections_by_id,
            get_all_tracks,
            add_all_tracks,
            remove_tracks,
            remove_section,
        )
        enable_filter_track_by_date = EnableFilterTrackByDate(
            self.track_view_state, filter_element_settings_restorer
        )
        create_default_filter = CreateDefaultFilterRange(
            state=self.track_view_state,
            videos_metadata=self.videos_metadata,
            enable_filter_track_by_date=enable_filter_track_by_date,
        )
        previous_frame = SwitchToPrevious(
            self.track_view_state, self.videos_metadata, create_default_filter
        )
        next_frame = SwitchToNext(
            self.track_view_state, self.videos_metadata, create_default_filter
        )
        switch_event = SwitchToEvent(
            event_repository=self.event_repository,
            track_view_state=self.track_view_state,
            section_state=self.section_state,
            create_default_filter=create_default_filter,
        )
        get_flows = GetAllFlows(self.flow_repository)
        save_otflow = SaveOtflow(
            self.flow_parser, get_sections, get_flows, self.file_state
        )
        get_current_remark = GetCurrentRemark(self.remark_repository)
        config_parser = self.create_config_parser()
        save_otconfig = SaveOtconfig(
            self.datastore, config_parser, self.file_state, get_current_remark
        )
        quick_save_configuration = QuickSaveConfiguration(
            self.file_state, save_otflow, save_otconfig
        )
        add_new_remark = AddNewRemark(self.remark_repository)
        load_otconfig = LoadOtconfig(
            clear_repositories,
            config_parser,
            project_updater,
            AddAllVideos(self.video_repository),
            AddAllSections(add_section),
            AddAllFlows(add_flow),
            load_track_files,
            add_new_remark,
            parse_json,
        )
        get_all_videos = GetAllVideos(self.video_repository)
        get_current_project = GetCurrentProject(self.datastore)
        config_has_changed = ConfigHasChanged(
            OtconfigHasChanged(
                config_parser,
                get_sections,
                get_flows,
                get_current_project,
                get_all_videos,
                get_all_track_files,
                get_current_remark,
            ),
            OtflowHasChanged(self.flow_parser, get_sections, get_flows),
            self.file_state,
        )
        export_road_user_assignments = self.create_export_road_user_assignments(
            get_all_tracks, create_events
        )
        save_path_suggester = SavePathSuggester(
            self.file_state, get_all_track_files, get_all_videos, get_current_project
        )
        tracks_intersecting_sections = self._create_tracks_intersecting_sections(
            get_all_tracks
        )

        calculate_track_statistics = self._create_calculate_track_statistics(
            get_sections,
            tracks_intersecting_sections,
            get_sections_by_id,
            get_all_tracks,
        )
        get_road_user_assignments = GetRoadUserAssignments(
            self.flow_repository, self.event_repository, self.road_user_assigner
        )
        number_of_tracks_assigned_to_each_flow = NumberOfTracksAssignedToEachFlow(
            get_road_user_assignments, self.flow_repository
        )
        track_statistics_export_factory = CachedTrackStatisticsExporterFactory(
            SimpleTrackStatisticsExporterFactory()
        )
        export_track_statistics = ExportTrackStatistics(
            calculate_track_statistics, track_statistics_export_factory
        )
        application = OTAnalyticsApplication(
            self.datastore,
            self.track_state,
            self.track_view_state,
            self.section_state,
            self.flow_state,
            self.file_state,
            tracks_metadata,
            self.videos_metadata,
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
            save_otconfig,
            load_track_files,
            enable_filter_track_by_date,
            previous_frame,
            next_frame,
            switch_event,
            save_otflow,
            quick_save_configuration,
            load_otconfig,
            config_has_changed,
            export_road_user_assignments,
            save_path_suggester,
            calculate_track_statistics,
            number_of_tracks_assigned_to_each_flow,
            export_track_statistics,
            get_current_remark,
        )
        self.section_repository.register_sections_observer(
            cut_tracks_intersecting_section
        )
        self.section_repository.register_section_changed_observer(
            cut_tracks_intersecting_section.notify_section_changed
        )
        cut_tracks_intersecting_section.register(clear_all_events.on_tracks_cut)
        application.connect_clear_event_repository_observer()
        name_generator = ArrowFlowNameGenerator()
        dummy_viewmodel = DummyViewModel(
            application,
            self.flow_parser,
            name_generator,
            event_list_export_formats=AVAILABLE_EVENTLIST_EXPORTERS,
            show_svz=self.run_config.show_svz,
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
        self.track_view_state.filter_date_active.register(
            dummy_viewmodel.change_filter_date_active
        )
        self.track_view_state.filter_element.register(
            self.selected_video_updater.on_filter_element_change
        )
        # TODO: Refactor observers - move registering to subjects happening in
        #   constructor dummy_viewmodel
        # cut_tracks_intersecting_section.register(
        #    cached_pandas_track_provider.on_tracks_cut
        # )
        cut_tracks_intersecting_section.register(dummy_viewmodel.on_tracks_cut)
        dummy_viewmodel.register_observers()
        application.connect_observers()
        self.datastore.register_tracks_observer(self.selected_video_updater)
        self.datastore.register_tracks_observer(dummy_viewmodel)
        self.datastore.register_tracks_observer(track_image_updater)
        self.datastore.register_video_observer(self.selected_video_updater)
        self.datastore.register_section_changed_observer(
            track_image_updater.notify_section_changed
        )
        start_new_project.register(dummy_viewmodel.on_start_new_project)
        self.event_repository.register_observer(track_image_updater.notify_events)
        self.event_repository.register_observer(dummy_viewmodel.update_track_statistics)
        load_otflow.register(self.file_state.last_saved_config.set)
        load_otconfig.register(self.file_state.last_saved_config.set)
        load_otconfig.register(dummy_viewmodel.update_remark_view)
        project_updater.register(dummy_viewmodel.update_quick_save_button)
        self.track_file_repository.register(dummy_viewmodel.update_quick_save_button)
        project_updater.register(dummy_viewmodel.show_current_project)
        project_updater.register(dummy_viewmodel.update_svz_metadata_view)

        for group in layer_groups:
            group.register(track_image_updater.notify_layers)
        main_window = ModifiedCTk(dummy_viewmodel)
        self.pulling_progressbar_popup_builder.add_widget(main_window)
        apply_cli_cuts = self.create_apply_cli_cuts(cut_tracks_intersecting_section)
        preload_input_files = self.create_preload_input_files(
            load_otconfig=load_otconfig,
            load_otflow=load_otflow,
            load_track_files=load_track_files,
            apply_cli_cuts=apply_cli_cuts,
        )
        OTAnalyticsGui(
            main_window,
            dummy_viewmodel,
            layer_groups,
            preload_input_files,
            self.run_config,
        ).start()

    @cached_property
    def selected_video_updater(self) -> SelectedVideoUpdate:
        return SelectedVideoUpdate(
            self.datastore, self.track_view_state, self.videos_metadata
        )

    def _create_track_image_updater(self, plotter: LayeredPlotter) -> TrackImageUpdater:
        return TrackImageUpdater(
            self.datastore,
            self.track_view_state,
            self.section_state,
            self.flow_state,
            plotter,
        )

    @cached_property
    def track_properties_updater(self) -> TrackPropertiesUpdater:
        return TrackPropertiesUpdater(self.datastore, self.track_view_state)

    @cached_property
    def clear_all_intersections(self) -> ClearAllIntersections:
        return ClearAllIntersections(self.intersection_repository)

    @cached_property
    def color_palette_provider(self) -> ColorPaletteProvider:
        return ColorPaletteProvider(DEFAULT_COLOR_PALETTE)

    @cached_property
    def road_user_assigner(self) -> RoadUserAssigner:
        return FilterBySectionEnterEvent(self.simple_road_user_assigner)

    @cached_property
    def simple_road_user_assigner(self) -> RoadUserAssigner:
        return SimpleRoadUserAssigner()

    @cached_property
    def file_state(self) -> FileState:
        return FileState()

    @cached_property
    def pulling_progressbar_builder(self) -> ProgressbarBuilder:
        from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_progress import (
            PullingProgressbarBuilder,
        )

        pulling_progressbar_builder = PullingProgressbarBuilder(
            self.pulling_progressbar_popup_builder
        )
        return pulling_progressbar_builder

    @cached_property
    def pulling_progressbar_popup_builder(self) -> ProgressbarPopupBuilder:
        from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_progress import (
            PullingProgressbarPopupBuilder,
        )

        pulling_progressbar_popup_builder = PullingProgressbarPopupBuilder()
        return pulling_progressbar_popup_builder

    @cached_property
    def videos_metadata(self) -> VideosMetadata:
        return VideosMetadata()

    def start_cli(self) -> None:
        add_section = AddSection(self.section_repository)
        get_sections_by_id = GetSectionsById(self.section_repository)
        get_all_sections = GetAllSections(self.section_repository)
        add_flow = AddFlow(self.flow_repository)
        add_events = AddEvents(self.event_repository)
        get_tracks_without_single_detections = GetTracksWithoutSingleDetections(
            self.track_repository
        )
        get_all_tracks = GetAllTracks(self.track_repository)
        get_all_track_ids = GetAllTrackIds(self.track_repository)
        clear_all_events = ClearAllEvents(self.event_repository)
        tracks_metadata = self._create_tracks_metadata()
        section_provider = FilterOutCuttingSections(self.section_repository.get_all)
        create_events = self._create_use_case_create_events(
            section_provider,
            clear_all_events,
            get_all_tracks,
            get_tracks_without_single_detections,
            add_events,
            self.run_config.num_processes,
        )
        cut_tracks = self._create_cut_tracks_intersecting_section(
            GetSectionsById(self.section_repository),
            get_all_tracks,
            AddAllTracks(self.track_repository),
            RemoveTracks(self.track_repository),
            RemoveSection(self.section_repository),
        )
        apply_cli_cuts = self.create_apply_cli_cuts(cut_tracks)
        add_all_tracks = AddAllTracks(self.track_repository)
        clear_all_tracks = ClearAllTracks(self.track_repository)
        export_counts = self._create_export_counts(get_sections_by_id, create_events)
        tracks_metadata = self._create_tracks_metadata()
        export_tracks = CsvTrackExport(
            self.track_repository, tracks_metadata, self.videos_metadata
        )
        export_road_user_assignments = self.create_export_road_user_assignments(
            get_all_tracks, create_events
        )
        get_sections = GetAllSections(self.section_repository)
        tracks_intersecting_sections = self._create_tracks_intersecting_sections(
            get_all_tracks
        )
        calculate_track_statistics = self._create_calculate_track_statistics(
            get_sections,
            tracks_intersecting_sections,
            get_sections_by_id,
            get_all_tracks,
        )
        track_statistics_export_factory = CachedTrackStatisticsExporterFactory(
            SimpleTrackStatisticsExporterFactory()
        )
        export_track_statistics = ExportTrackStatistics(
            calculate_track_statistics, track_statistics_export_factory
        )

        cli: OTAnalyticsCli
        if self.run_config.cli_bulk_mode:
            track_parser = self._create_track_parser()

            cli = OTAnalyticsBulkCli(
                self.run_config,
                self.event_repository,
                add_section,
                get_all_sections,
                add_flow,
                create_events,
                export_counts,
                provide_available_eventlist_exporter,
                apply_cli_cuts,
                add_all_tracks,
                get_all_track_ids,
                clear_all_tracks,
                tracks_metadata,
                self.videos_metadata,
                export_tracks,
                export_road_user_assignments,
                export_track_statistics,
                track_parser,
                progressbar=TqdmBuilder(),
            )

        else:
            stream_track_parser = self._create_stream_track_parser()
            cli = OTAnalyticsStreamCli(
                self.run_config,
                self.event_repository,
                add_section,
                get_all_sections,
                add_flow,
                create_events,
                export_counts,
                export_track_statistics,
                provide_available_eventlist_exporter,
                apply_cli_cuts,
                add_all_tracks,
                get_all_track_ids,
                clear_all_tracks,
                tracks_metadata,
                self.videos_metadata,
                export_tracks,
                export_road_user_assignments,
                stream_track_parser,
            )

        cli.start()

    @cached_property
    def datastore(self) -> Datastore:
        """
        Build all required objects and inject them where necessary

        """
        track_parser = self._create_track_parser()
        event_list_parser = self._create_event_list_parser()
        track_video_parser = OttrkVideoParser(self.video_parser)
        return Datastore(
            self.track_repository,
            self.track_file_repository,
            track_parser,
            self.section_repository,
            self.flow_repository,
            self.event_repository,
            event_list_parser,
            self.track_to_video_repository,
            self.video_repository,
            self.video_parser,
            track_video_parser,
            self.pulling_progressbar_builder,
            self.remark_repository,
        )

    @cached_property
    def track_repository(self) -> TrackRepository:
        return TrackRepository(
            FilteredPandasTrackDataset(
                PandasTrackDataset.from_list(
                    [], PygeosTrackGeometryDataset.from_track_dataset
                ),
                self.run_config.include_classes,
                self.run_config.exclude_classes,
            )
        )

    def _create_track_parser(self) -> TrackParser:
        calculator = PandasByMaxConfidence()
        detection_parser = PandasDetectionParser(
            calculator,
            PygeosTrackGeometryDataset.from_track_dataset,
            track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT,
        )
        return OttrkParser(detection_parser)

    def _create_stream_track_parser(self) -> StreamTrackParser:
        return StreamOttrkParser(
            detection_parser=PythonStreamDetectionParser(
                track_classification_calculator=ByMaxConfidence(),
                track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT,
            ),
            format_fixer=OttrkFormatFixer(),
            progressbar=TqdmBuilder(),
            track_dataset_factory=lambda tracks: PandasTrackDataset.from_list(
                tracks,
                PygeosTrackGeometryDataset.from_track_dataset,
                PandasByMaxConfidence(),
            ),
            chunk_size=self.run_config.cli_chunk_size,
        )

    @cached_property
    def section_repository(self) -> SectionRepository:
        return SectionRepository()

    @cached_property
    def flow_parser(self) -> FlowParser:
        return OtFlowParser()

    @cached_property
    def flow_repository(self) -> FlowRepository:
        return FlowRepository()

    @cached_property
    def intersection_repository(self) -> IntersectionRepository:
        return PythonIntersectionRepository()

    @cached_property
    def event_repository(self) -> EventRepository:
        return EventRepository()

    def _create_event_list_parser(self) -> EventListParser:
        return OtEventListParser()

    @cached_property
    def track_state(self) -> TrackState:
        return TrackState()

    @cached_property
    def track_view_state(self) -> TrackViewState:
        return TrackViewState()

    def _create_layers(self) -> tuple[Sequence[LayerGroup], Sequence[PlottingLayer]]:
        return VisualizationBuilder(
            self.datastore,
            self.intersection_repository,
            self.track_view_state,
            self.videos_metadata,
            self.section_state,
            self.color_palette_provider,
            self.pulling_progressbar_builder,
        ).build(
            self.flow_state,
            self.road_user_assigner,
        )

    @cached_property
    def section_state(self) -> SectionState:
        return SectionState(GetSectionsById(self.section_repository))

    @cached_property
    def flow_state(self) -> FlowState:
        return FlowState()

    def _create_get_all_track_files(self) -> GetAllTrackFiles:
        return GetAllTrackFiles(self.track_file_repository)

    def _create_flow_generator(
        self, section_provider: SectionProvider
    ) -> GenerateFlows:
        id_generator: FlowIdGenerator = RepositoryFlowIdGenerator(self.flow_repository)
        name_generator = ArrowFlowNameGenerator()
        flow_generator = CrossProductFlowGenerator(
            id_generator=id_generator,
            name_generator=name_generator,
            predicate=FilterSameSection().and_then(
                FilterExisting(self.flow_repository)
            ),
        )
        return GenerateFlows(
            section_provider=section_provider,
            flow_repository=self.flow_repository,
            flow_generator=flow_generator,
        )

    def _create_use_case_create_intersection_events(
        self,
        section_provider: SectionProvider,
        get_tracks: GetAllTracks,
        add_events: AddEvents,
        num_processes: int,
    ) -> CreateIntersectionEvents:
        intersect = self._create_intersect(get_tracks, num_processes)
        return SimpleCreateIntersectionEvents(intersect, section_provider, add_events)

    @staticmethod
    def _create_intersect(get_tracks: GetAllTracks, num_processes: int) -> RunIntersect:
        return BatchedTracksRunIntersect(
            intersect_parallelizer=MultiprocessingIntersectParallelization(
                num_processes
            ),
            get_tracks=get_tracks,
        )

    def _create_tracks_metadata(self) -> TracksMetadata:
        return TracksMetadata(
            self.track_repository,
            self.run_config.include_classes,
            self.run_config.exclude_classes,
        )

    def _create_action_state(self) -> ActionState:
        return ActionState()

    def _create_filter_element_setting_restorer(self) -> FilterElementSettingRestorer:
        return FilterElementSettingRestorer()

    def _create_export_counts(
        self, get_sections_by_id: GetSectionsById, create_events: CreateEvents
    ) -> ExportCounts:
        return ExportTrafficCounting(
            self.event_repository,
            self.flow_repository,
            get_sections_by_id,
            create_events,
            self.road_user_assigner,
            SimpleTaggerFactory(),
            CachedExporterFactory(
                FillZerosExporterFactory(
                    AddSectionInformationExporterFactory(SimpleExporterFactory())
                ),
            ),
        )

    def _create_use_case_create_events(
        self,
        section_provider: SectionProvider,
        clear_events: ClearAllEvents,
        get_all_tracks: GetAllTracks,
        get_all_tracks_without_single_detections: GetTracksWithoutSingleDetections,
        add_events: AddEvents,
        num_processes: int,
    ) -> CreateEvents:
        run_intersect = self._create_intersect(get_all_tracks, num_processes)
        create_intersection_events = SimpleCreateIntersectionEvents(
            run_intersect, section_provider, add_events
        )
        scene_action_detector = SceneActionDetector()
        create_scene_events = SimpleCreateSceneEvents(
            get_all_tracks_without_single_detections, scene_action_detector, add_events
        )
        return CreateEvents(
            clear_events, create_intersection_events, create_scene_events
        )

    @staticmethod
    def _create_tracks_intersecting_sections(
        get_tracks: GetAllTracks,
    ) -> TracksIntersectingSections:
        return SimpleTracksIntersectingSections(get_tracks)

    def _create_use_case_load_otflow(
        self,
        clear_all_sections: ClearAllSections,
        clear_all_flows: ClearAllFlows,
        clear_all_events: ClearAllEvents,
        add_section: AddSection,
        add_flow: AddFlow,
    ) -> LoadOtflow:
        return LoadOtflow(
            clear_all_sections,
            clear_all_flows,
            clear_all_events,
            self.flow_parser,
            add_section,
            add_flow,
            parse_json,
        )

    def _create_use_case_clear_all_repositories(
        self,
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
            self.clear_all_intersections,
            clear_all_sections,
            clear_all_track_to_videos,
            clear_all_tracks,
            clear_all_videos,
        )

    def _create_use_case_start_new_project(
        self,
        clear_repositories: ClearRepositories,
        reset_project_config: ResetProjectConfig,
    ) -> StartNewProject:
        return StartNewProject(
            clear_repositories,
            reset_project_config,
            self.track_view_state,
            self.file_state,
        )

    @staticmethod
    def _create_reset_project_config(
        project_updater: ProjectUpdater,
    ) -> ResetProjectConfig:
        return ResetProjectConfig(project_updater)

    def _create_project_updater(self) -> ProjectUpdater:
        return ProjectUpdater(self.datastore)

    @cached_property
    def track_file_repository(self) -> TrackFileRepository:
        return TrackFileRepository()

    @staticmethod
    def _create_cut_tracks_intersecting_section(
        get_sections_by_id: GetSectionsById,
        get_tracks: GetAllTracks,
        add_all_tracks: AddAllTracks,
        remove_tracks: RemoveTracks,
        remove_section: RemoveSection,
    ) -> CutTracksIntersectingSection:
        return SimpleCutTracksIntersectingSection(
            get_sections_by_id,
            get_tracks,
            add_all_tracks,
            remove_tracks,
            remove_section,
        )

    def _create_load_tracks_file(
        self, tracks_metadata: TracksMetadata
    ) -> LoadTrackFiles:
        track_parser = self._create_track_parser()
        track_video_parser = OttrkVideoParser(self.video_parser)
        return LoadTrackFiles(
            track_parser,
            track_video_parser,
            self.track_repository,
            self.track_file_repository,
            self.video_repository,
            self.track_to_video_repository,
            self.pulling_progressbar_builder,
            tracks_metadata,
            self.videos_metadata,
        )

    @cached_property
    def video_parser(self) -> VideoParser:
        return CachedVideoParser(
            SimpleVideoParser(PyAvVideoReader(self.videos_metadata))
        )

    @cached_property
    def remark_repository(self) -> RemarkRepository:
        return RemarkRepository()

    @cached_property
    def video_repository(self) -> VideoRepository:
        return VideoRepository()

    @cached_property
    def track_to_video_repository(self) -> TrackToVideoRepository:
        return TrackToVideoRepository()

    def create_preload_input_files(
        self,
        load_otconfig: LoadOtconfig,
        load_otflow: LoadOtflow,
        load_track_files: LoadTrackFiles,
        apply_cli_cuts: ApplyCliCuts,
    ) -> PreloadInputFiles:
        return PreloadInputFiles(
            load_track_files=load_track_files,
            load_otconfig=load_otconfig,
            load_otflow=load_otflow,
            apply_cli_cuts=apply_cli_cuts,
        )

    def create_apply_cli_cuts(
        self, cut_tracks: CutTracksIntersectingSection
    ) -> ApplyCliCuts:
        return ApplyCliCuts(cut_tracks, TrackRepositorySize(self.track_repository))

    def create_config_parser(self) -> OtConfigParser:
        format_fixer = self._create_format_fixer(self.run_config)
        return OtConfigParser(
            video_parser=self.video_parser,
            flow_parser=self.flow_parser,
            format_fixer=format_fixer,
        )

    def create_export_road_user_assignments(
        self, get_all_tracks: GetAllTracks, create_events: CreateEvents
    ) -> ExportRoadUserAssignments:
        return ExportRoadUserAssignments(
            self.event_repository,
            self.flow_repository,
            create_events,
            self.road_user_assigner,
            SimpleRoadUserAssignmentExporterFactory(
                self.section_repository, get_all_tracks
            ),
        )

    def _create_calculate_track_statistics(
        self,
        get_all_sections: GetAllSections,
        tracks_intersecting_sections: TracksIntersectingSections,
        get_section_by_id: GetSectionsById,
        get_all_tracks: GetAllTracks,
    ) -> CalculateTrackStatistics:
        get_cutting_sections = GetCuttingSections(self.section_repository)
        tracks_intersecting_all_sections = TracksIntersectingAllNonCuttingSections(
            get_cutting_sections,
            get_all_sections,
            tracks_intersecting_sections,
            get_section_by_id,
            self.intersection_repository,
        )
        tracks_assigned_to_all_flows = TracksAssignedToAllFlows(
            self.road_user_assigner, self.event_repository, self.flow_repository
        )
        track_ids_inside_cutting_sections = TrackIdsInsideCuttingSections(
            get_all_tracks, get_cutting_sections
        )
        get_all_track_ids = GetAllTrackIds(self.track_repository)
        tracks_as_dataframe_provider = TracksAsDataFrameProvider(
            get_all_tracks=get_all_tracks,
            track_geometry_factory=PygeosTrackGeometryDataset.from_track_dataset,
        )
        detection_rate_strategy = DetectionRateByPercentile(
            percentile_value=DETECTION_RATE_PERCENTILE_VALUE
        )
        metric_rates_builder = MetricRatesBuilder(SVZ_CLASSIFICATION)
        number_of_tracks_to_be_validated = SvzNumberOfTracksToBeValidated(
            tracks_provider=tracks_as_dataframe_provider,
            tracks_assigned_to_all_flows=tracks_assigned_to_all_flows,
            detection_rate_strategy=detection_rate_strategy,
            metric_rates_builder=metric_rates_builder,
        )
        get_events = GetAllEnterSectionEvents(event_repository=self.event_repository)
        return CalculateTrackStatistics(
            tracks_intersecting_all_sections,
            tracks_assigned_to_all_flows,
            get_all_track_ids,
            track_ids_inside_cutting_sections,
            number_of_tracks_to_be_validated,
            get_events,
        )
