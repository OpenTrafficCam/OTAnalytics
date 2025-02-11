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
    CreateDefaultFilter,
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
    FlowNameGenerator,
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
    TrackStatisticsExporterFactory,
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

        # TODO: Should not register to tracks_metadata._classifications but to
        # TODO: ottrk metadata detection classes
        self.tracks_metadata._classifications.register(
            observer=self.color_palette_provider.update
        )

        create_events = self._create_use_case_create_events(
            self.section_provider_event_creation_ui,
            self.clear_all_events,
            self.get_tracks_without_single_detections,
            DEFAULT_NUM_PROCESSES,
        )
        intersect_tracks_with_sections = (
            self._create_use_case_create_intersection_events(
                self.section_provider_event_creation_ui,
                self.get_all_tracks,
                DEFAULT_NUM_PROCESSES,
            )
        )
        export_counts = self._create_export_counts(create_events)
        export_road_user_assignments = self.create_export_road_user_assignments(
            create_events
        )
        application = OTAnalyticsApplication(
            self.datastore,
            self.track_state,
            self.track_view_state,
            self.section_state,
            self.flow_state,
            self.file_state,
            self.tracks_metadata,
            self.videos_metadata,
            self.action_state,
            self.filter_element_settings_restorer,
            self.get_all_track_files,
            self.flow_generator,
            intersect_tracks_with_sections,
            export_counts,
            create_events,
            self.load_otflow,
            self.add_section,
            self.add_flow,
            self.clear_all_events,
            self.start_new_project,
            self.project_updater,
            self.save_otconfig,
            self.load_track_files,
            self.enable_filter_track_by_date,
            self.switch_to_previous,
            self.switch_to_next,
            self.switch_to_event,
            self.save_otflow,
            self.quick_save_configuration,
            self.load_otconfig,
            self.config_has_changed,
            export_road_user_assignments,
            self.save_path_suggester,
            self.calculate_track_statistics,
            self.number_of_tracks_assigned_to_each_flow,
            self.export_track_statistics,
            self.get_current_remark,
        )
        self.section_repository.register_sections_observer(
            self.cut_tracks_intersecting_section
        )
        self.section_repository.register_section_changed_observer(
            self.cut_tracks_intersecting_section.notify_section_changed
        )
        self.cut_tracks_intersecting_section.register(
            self.clear_all_events.on_tracks_cut
        )
        application.connect_clear_event_repository_observer()
        dummy_viewmodel = DummyViewModel(
            application,
            self.flow_parser,
            self.name_generator,
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
        self.cut_tracks_intersecting_section.register(dummy_viewmodel.on_tracks_cut)
        dummy_viewmodel.register_observers()
        application.connect_observers()
        self.datastore.register_tracks_observer(self.selected_video_updater)
        self.datastore.register_tracks_observer(dummy_viewmodel)
        self.datastore.register_tracks_observer(track_image_updater)
        self.datastore.register_video_observer(self.selected_video_updater)
        self.datastore.register_section_changed_observer(
            track_image_updater.notify_section_changed
        )
        self.start_new_project.register(dummy_viewmodel.on_start_new_project)
        self.event_repository.register_observer(track_image_updater.notify_events)
        self.event_repository.register_observer(dummy_viewmodel.update_track_statistics)
        self.load_otflow.register(self.file_state.last_saved_config.set)
        self.load_otconfig.register(self.file_state.last_saved_config.set)
        self.load_otconfig.register(dummy_viewmodel.update_remark_view)
        self.project_updater.register(dummy_viewmodel.update_quick_save_button)
        self.track_file_repository.register(dummy_viewmodel.update_quick_save_button)
        self.project_updater.register(dummy_viewmodel.show_current_project)
        self.project_updater.register(dummy_viewmodel.update_svz_metadata_view)

        for group in layer_groups:
            group.register(track_image_updater.notify_layers)
        main_window = ModifiedCTk(dummy_viewmodel)
        self.pulling_progressbar_popup_builder.add_widget(main_window)
        preload_input_files = self.create_preload_input_files()
        OTAnalyticsGui(
            main_window,
            dummy_viewmodel,
            layer_groups,
            preload_input_files,
            self.run_config,
        ).start()

    @cached_property
    def name_generator(self) -> FlowNameGenerator:
        return ArrowFlowNameGenerator()

    @cached_property
    def export_track_statistics(self) -> ExportTrackStatistics:
        return ExportTrackStatistics(
            self.calculate_track_statistics, self.track_statistics_export_factory
        )

    @cached_property
    def track_statistics_export_factory(self) -> TrackStatisticsExporterFactory:
        return CachedTrackStatisticsExporterFactory(
            SimpleTrackStatisticsExporterFactory()
        )

    @cached_property
    def number_of_tracks_assigned_to_each_flow(
        self,
    ) -> NumberOfTracksAssignedToEachFlow:
        return NumberOfTracksAssignedToEachFlow(
            self.get_road_user_assignments, self.flow_repository
        )

    @cached_property
    def get_road_user_assignments(self) -> GetRoadUserAssignments:
        return GetRoadUserAssignments(
            self.flow_repository, self.event_repository, self.road_user_assigner
        )

    @cached_property
    def save_path_suggester(self) -> SavePathSuggester:
        return SavePathSuggester(
            self.file_state,
            self.get_all_track_files,
            self.get_all_videos,
            self.get_current_project,
        )

    @cached_property
    def config_has_changed(self) -> ConfigHasChanged:
        return ConfigHasChanged(
            OtconfigHasChanged(
                self.otconfig_parser,
                self.get_all_sections,
                self.get_all_flows,
                self.get_current_project,
                self.get_all_videos,
                self.get_all_track_files,
                self.get_current_remark,
            ),
            OtflowHasChanged(
                self.flow_parser, self.get_all_sections, self.get_all_flows
            ),
            self.file_state,
        )

    @cached_property
    def get_current_project(self) -> GetCurrentProject:
        return GetCurrentProject(self.datastore)

    @cached_property
    def get_all_videos(self) -> GetAllVideos:
        return GetAllVideos(self.video_repository)

    @cached_property
    def load_otconfig(self) -> LoadOtconfig:
        return LoadOtconfig(
            self.clear_all_repositories,
            self.otconfig_parser,
            self.project_updater,
            AddAllVideos(self.video_repository),
            AddAllSections(self.add_section),
            AddAllFlows(self.add_flow),
            self.load_track_files,
            self.add_new_remark,
            parse_json,
        )

    @cached_property
    def add_new_remark(self) -> AddNewRemark:
        return AddNewRemark(self.remark_repository)

    @cached_property
    def quick_save_configuration(self) -> QuickSaveConfiguration:
        return QuickSaveConfiguration(
            self.file_state, self.save_otflow, self.save_otconfig
        )

    @cached_property
    def save_otconfig(self) -> SaveOtconfig:
        return SaveOtconfig(
            self.datastore,
            self.otconfig_parser,
            self.file_state,
            self.get_current_remark,
        )

    @cached_property
    def get_current_remark(self) -> GetCurrentRemark:
        return GetCurrentRemark(self.remark_repository)

    @cached_property
    def save_otflow(self) -> SaveOtflow:
        return SaveOtflow(
            self.flow_parser, self.get_all_sections, self.get_all_flows, self.file_state
        )

    @cached_property
    def get_all_flows(self) -> GetAllFlows:
        return GetAllFlows(self.flow_repository)

    @cached_property
    def switch_to_event(self) -> SwitchToEvent:
        return SwitchToEvent(
            event_repository=self.event_repository,
            track_view_state=self.track_view_state,
            section_state=self.section_state,
            create_default_filter=self.create_default_filter_range,
        )

    @cached_property
    def switch_to_next(self) -> SwitchToNext:
        return SwitchToNext(
            self.track_view_state,
            self.videos_metadata,
            self.create_default_filter_range,
        )

    @cached_property
    def switch_to_previous(self) -> SwitchToPrevious:
        return SwitchToPrevious(
            self.track_view_state,
            self.videos_metadata,
            self.create_default_filter_range,
        )

    @cached_property
    def create_default_filter_range(self) -> CreateDefaultFilter:
        return CreateDefaultFilterRange(
            state=self.track_view_state,
            videos_metadata=self.videos_metadata,
            enable_filter_track_by_date=self.enable_filter_track_by_date,
        )

    @cached_property
    def enable_filter_track_by_date(self) -> EnableFilterTrackByDate:
        return EnableFilterTrackByDate(
            self.track_view_state, self.filter_element_settings_restorer
        )

    @cached_property
    def section_provider_event_creation_ui(self) -> SectionProvider:
        return FilterOutCuttingSections(
            MissingEventsSectionProvider(self.section_repository, self.event_repository)
        )

    @cached_property
    def clear_all_track_to_videos(self) -> ClearAllTrackToVideos:
        return ClearAllTrackToVideos(self.track_to_video_repository)

    @cached_property
    def clear_all_videos(self) -> ClearAllVideos:
        return ClearAllVideos(self.video_repository)

    @cached_property
    def clear_all_events(self) -> ClearAllEvents:
        return ClearAllEvents(self.event_repository)

    @cached_property
    def add_events(self) -> AddEvents:
        return AddEvents(self.event_repository)

    @cached_property
    def clear_all_flows(self) -> ClearAllFlows:
        return ClearAllFlows(self.flow_repository)

    @cached_property
    def add_flow(self) -> AddFlow:
        return AddFlow(self.flow_repository)

    @cached_property
    def clear_all_sections(self) -> ClearAllSections:
        return ClearAllSections(self.section_repository)

    @cached_property
    def remove_section(self) -> RemoveSection:
        return RemoveSection(self.section_repository)

    @cached_property
    def add_section(self) -> AddSection:
        return AddSection(self.section_repository)

    @cached_property
    def get_sections_by_id(self) -> GetSectionsById:
        return GetSectionsById(self.section_repository)

    @cached_property
    def get_all_sections(self) -> GetAllSections:
        return GetAllSections(self.section_repository)

    @cached_property
    def clear_all_tracks(self) -> ClearAllTracks:
        return ClearAllTracks(self.track_repository)

    @cached_property
    def remove_tracks(self) -> RemoveTracks:
        return RemoveTracks(self.track_repository)

    @cached_property
    def add_all_tracks(self) -> AddAllTracks:
        return AddAllTracks(self.track_repository)

    @cached_property
    def get_tracks_without_single_detections(self) -> GetTracksWithoutSingleDetections:
        return GetTracksWithoutSingleDetections(self.track_repository)

    @cached_property
    def get_all_tracks(self) -> GetAllTracks:
        return GetAllTracks(self.track_repository)

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
        get_all_track_ids = GetAllTrackIds(self.track_repository)
        section_provider = FilterOutCuttingSections(self.section_repository.get_all)
        create_events = self._create_use_case_create_events(
            section_provider,
            self.clear_all_events,
            self.get_tracks_without_single_detections,
            self.run_config.num_processes,
        )
        export_counts = self._create_export_counts(create_events)
        export_tracks = CsvTrackExport(
            self.track_repository, self.tracks_metadata, self.videos_metadata
        )
        export_road_user_assignments = self.create_export_road_user_assignments(
            create_events
        )

        cli: OTAnalyticsCli
        if self.run_config.cli_bulk_mode:
            track_parser = self._create_track_parser()

            cli = OTAnalyticsBulkCli(
                self.run_config,
                self.event_repository,
                self.add_section,
                self.get_all_sections,
                self.add_flow,
                create_events,
                export_counts,
                provide_available_eventlist_exporter,
                self.apply_cli_cuts,
                self.add_all_tracks,
                get_all_track_ids,
                self.clear_all_tracks,
                self.tracks_metadata,
                self.videos_metadata,
                export_tracks,
                export_road_user_assignments,
                self.export_track_statistics,
                track_parser,
                progressbar=TqdmBuilder(),
            )

        else:
            stream_track_parser = self._create_stream_track_parser()
            cli = OTAnalyticsStreamCli(
                self.run_config,
                self.event_repository,
                self.add_section,
                self.get_all_sections,
                self.add_flow,
                create_events,
                export_counts,
                self.export_track_statistics,
                provide_available_eventlist_exporter,
                self.apply_cli_cuts,
                self.add_all_tracks,
                get_all_track_ids,
                self.clear_all_tracks,
                self.tracks_metadata,
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
        return SectionState(self.get_sections_by_id)

    @cached_property
    def flow_state(self) -> FlowState:
        return FlowState()

    @cached_property
    def get_all_track_files(self) -> GetAllTrackFiles:
        return GetAllTrackFiles(self.track_file_repository)

    @cached_property
    def flow_generator(self) -> GenerateFlows:
        section_provider = FilterOutCuttingSections(self.get_all_sections)
        id_generator: FlowIdGenerator = RepositoryFlowIdGenerator(self.flow_repository)
        flow_generator = CrossProductFlowGenerator(
            id_generator=id_generator,
            name_generator=self.name_generator,
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
        num_processes: int,
    ) -> CreateIntersectionEvents:
        intersect = self._create_intersect(get_tracks, num_processes)
        return SimpleCreateIntersectionEvents(
            intersect, section_provider, self.add_events
        )

    @staticmethod
    def _create_intersect(get_tracks: GetAllTracks, num_processes: int) -> RunIntersect:
        return BatchedTracksRunIntersect(
            intersect_parallelizer=MultiprocessingIntersectParallelization(
                num_processes
            ),
            get_tracks=get_tracks,
        )

    @cached_property
    def tracks_metadata(self) -> TracksMetadata:
        return TracksMetadata(
            self.track_repository,
            self.run_config.include_classes,
            self.run_config.exclude_classes,
        )

    @cached_property
    def action_state(self) -> ActionState:
        return ActionState()

    @cached_property
    def filter_element_settings_restorer(self) -> FilterElementSettingRestorer:
        return FilterElementSettingRestorer()

    def _create_export_counts(self, create_events: CreateEvents) -> ExportCounts:
        return ExportTrafficCounting(
            self.event_repository,
            self.flow_repository,
            self.get_sections_by_id,
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
        get_all_tracks_without_single_detections: GetTracksWithoutSingleDetections,
        num_processes: int,
    ) -> CreateEvents:
        run_intersect = self._create_intersect(self.get_all_tracks, num_processes)
        create_intersection_events = SimpleCreateIntersectionEvents(
            run_intersect, section_provider, self.add_events
        )
        scene_action_detector = SceneActionDetector()
        create_scene_events = SimpleCreateSceneEvents(
            get_all_tracks_without_single_detections,
            scene_action_detector,
            self.add_events,
        )
        return CreateEvents(
            clear_events, create_intersection_events, create_scene_events
        )

    @cached_property
    def tracks_intersecting_sections(self) -> TracksIntersectingSections:
        return SimpleTracksIntersectingSections(self.get_all_tracks)

    @cached_property
    def load_otflow(self) -> LoadOtflow:
        return LoadOtflow(
            self.clear_all_sections,
            self.clear_all_flows,
            self.clear_all_events,
            self.flow_parser,
            self.add_section,
            self.add_flow,
            parse_json,
        )

    @cached_property
    def clear_all_repositories(self) -> ClearRepositories:
        return ClearRepositories(
            self.clear_all_events,
            self.clear_all_flows,
            self.clear_all_intersections,
            self.clear_all_sections,
            self.clear_all_track_to_videos,
            self.clear_all_tracks,
            self.clear_all_videos,
        )

    @cached_property
    def start_new_project(self) -> StartNewProject:
        return StartNewProject(
            self.clear_all_repositories,
            self.reset_project_config,
            self.track_view_state,
            self.file_state,
        )

    @cached_property
    def reset_project_config(self) -> ResetProjectConfig:
        return ResetProjectConfig(self.project_updater)

    @cached_property
    def project_updater(self) -> ProjectUpdater:
        return ProjectUpdater(self.datastore)

    @cached_property
    def track_file_repository(self) -> TrackFileRepository:
        return TrackFileRepository()

    @cached_property
    def cut_tracks_intersecting_section(self) -> CutTracksIntersectingSection:
        return SimpleCutTracksIntersectingSection(
            self.get_sections_by_id,
            self.get_all_tracks,
            self.add_all_tracks,
            self.remove_tracks,
            self.remove_section,
        )

    @cached_property
    def load_track_files(self) -> LoadTrackFiles:
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
            self.tracks_metadata,
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

    def create_preload_input_files(self) -> PreloadInputFiles:
        return PreloadInputFiles(
            load_track_files=self.load_track_files,
            load_otconfig=self.load_otconfig,
            load_otflow=self.load_otflow,
            apply_cli_cuts=self.apply_cli_cuts,
        )

    @cached_property
    def apply_cli_cuts(self) -> ApplyCliCuts:
        return ApplyCliCuts(
            self.cut_tracks_intersecting_section,
            TrackRepositorySize(self.track_repository),
        )

    @cached_property
    def otconfig_parser(self) -> OtConfigParser:
        format_fixer = self._create_format_fixer(self.run_config)
        return OtConfigParser(
            video_parser=self.video_parser,
            flow_parser=self.flow_parser,
            format_fixer=format_fixer,
        )

    def create_export_road_user_assignments(
        self, create_events: CreateEvents
    ) -> ExportRoadUserAssignments:
        return ExportRoadUserAssignments(
            self.event_repository,
            self.flow_repository,
            create_events,
            self.road_user_assigner,
            SimpleRoadUserAssignmentExporterFactory(
                self.section_repository, self.get_all_tracks
            ),
        )

    @cached_property
    def calculate_track_statistics(self) -> CalculateTrackStatistics:
        get_cutting_sections = GetCuttingSections(self.section_repository)
        tracks_intersecting_all_sections = TracksIntersectingAllNonCuttingSections(
            get_cutting_sections,
            self.get_all_sections,
            self.tracks_intersecting_sections,
            self.get_sections_by_id,
            self.intersection_repository,
        )
        tracks_assigned_to_all_flows = TracksAssignedToAllFlows(
            self.road_user_assigner, self.event_repository, self.flow_repository
        )
        track_ids_inside_cutting_sections = TrackIdsInsideCuttingSections(
            self.get_all_tracks, get_cutting_sections
        )
        get_all_track_ids = GetAllTrackIds(self.track_repository)
        tracks_as_dataframe_provider = TracksAsDataFrameProvider(
            get_all_tracks=self.get_all_tracks,
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
