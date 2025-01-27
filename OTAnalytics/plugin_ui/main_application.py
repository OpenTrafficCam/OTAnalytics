import logging
from pathlib import Path
from typing import Sequence

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
        run_config = self._parse_configuration()
        self._setup_logger(
            Path(run_config.log_file), run_config.logfile_overwrite, run_config.debug
        )
        if run_config.start_cli:
            try:

                self.start_cli(run_config)
                # add command line tag for activating -> add to PipelineBenchmark,
                # add github actions for benchmark
                # regression test lokal runner neben benchmark ->
                # OTC -> test data -> 6-1145, flow in 00 -> in test resource ordner

            except CliParseError as e:
                logger().exception(e, exc_info=True)
        else:
            self.start_gui(run_config)

    def _parse_configuration(self) -> RunConfiguration:
        cli_args_parser = self._build_cli_argument_parser()
        cli_args = cli_args_parser.parse()
        cli_value_provider: OtConfigDefaultValueProvider = CliValueProvider(cli_args)
        format_fixer = self._create_format_fixer(cli_value_provider)
        flow_parser = self._create_flow_parser()
        config_parser = OtConfigParser(
            format_fixer=format_fixer,
            video_parser=self._create_video_parser(VideosMetadata()),
            flow_parser=flow_parser,
        )

        if config_file := cli_args.config_file:
            config = config_parser.parse(Path(config_file))
            return RunConfiguration(flow_parser, cli_args, config)
        return RunConfiguration(flow_parser, cli_args, None)

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

    def start_gui(self, run_config: RunConfiguration) -> None:
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

        track_repository = self._create_track_repository(run_config)
        track_file_repository = self._create_track_file_repository()
        section_repository = self._create_section_repository()
        flow_repository = self._create_flow_repository()
        intersection_repository = self._create_intersection_repository()
        event_repository = self._create_event_repository()
        videos_metadata = VideosMetadata()
        video_parser = self._create_video_parser(videos_metadata)
        video_repository = self._create_video_repository()
        remark_repository = self._create_remark_repository()
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
            remark_repository,
        )
        flow_parser = self._create_flow_parser()
        track_state = self._create_track_state()
        track_view_state = self._create_track_view_state()
        section_state = self._create_section_state(section_repository)
        flow_state = self._create_flow_state()
        file_state = FileState()
        road_user_assigner = FilterBySectionEnterEvent(SimpleRoadUserAssigner())
        color_palette_provider = ColorPaletteProvider(DEFAULT_COLOR_PALETTE)
        clear_all_intersections = ClearAllIntersections(intersection_repository)
        track_repository.register_tracks_observer(clear_all_intersections)
        section_repository.register_sections_observer(clear_all_intersections)
        section_repository.register_section_changed_observer(
            clear_all_intersections.on_section_changed
        )
        layer_groups, layers = self._create_layers(
            datastore,
            intersection_repository,
            track_view_state,
            videos_metadata,
            flow_state,
            section_state,
            pulling_progressbar_builder,
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
        selected_video_updater = SelectedVideoUpdate(
            datastore, track_view_state, videos_metadata
        )

        tracks_metadata = self._create_tracks_metadata(track_repository, run_config)
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
        get_all_tracks = GetAllTracks(track_repository)
        get_tracks_without_single_detections = GetTracksWithoutSingleDetections(
            track_repository
        )
        add_all_tracks = AddAllTracks(track_repository)
        remove_tracks = RemoveTracks(track_repository)
        clear_all_tracks = ClearAllTracks(track_repository)

        get_sections_by_id = GetSectionsById(section_repository)
        add_section = AddSection(section_repository)
        remove_section = RemoveSection(section_repository)
        clear_all_sections = ClearAllSections(section_repository)
        section_provider = FilterOutCuttingSections(
            MissingEventsSectionProvider(section_repository, event_repository)
        )
        generate_flows = self._create_flow_generator(section_provider, flow_repository)
        add_flow = AddFlow(flow_repository)
        clear_all_flows = ClearAllFlows(flow_repository)

        add_events = AddEvents(event_repository)
        clear_all_events = ClearAllEvents(event_repository)

        clear_all_videos = ClearAllVideos(datastore._video_repository)
        clear_all_track_to_videos = ClearAllTrackToVideos(
            datastore._track_to_video_repository
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
        export_counts = self._create_export_counts(
            event_repository,
            flow_repository,
            # track_repository,
            get_sections_by_id,
            create_events,
        )
        load_otflow = self._create_use_case_load_otflow(
            clear_all_sections,
            clear_all_flows,
            clear_all_events,
            flow_parser,
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
            videos_metadata,
        )
        clear_repositories = self._create_use_case_clear_all_repositories(
            clear_all_events,
            clear_all_flows,
            clear_all_intersections,
            clear_all_sections,
            clear_all_track_to_videos,
            clear_all_tracks,
            clear_all_videos,
        )
        project_updater = self._create_project_updater(datastore)
        reset_project_config = self._create_reset_project_config(project_updater)
        start_new_project = self._create_use_case_start_new_project(
            clear_repositories, reset_project_config, track_view_state, file_state
        )
        cut_tracks_intersecting_section = self._create_cut_tracks_intersecting_section(
            get_sections_by_id,
            get_all_tracks,
            add_all_tracks,
            remove_tracks,
            remove_section,
        )
        enable_filter_track_by_date = EnableFilterTrackByDate(
            track_view_state, filter_element_settings_restorer
        )
        create_default_filter = CreateDefaultFilterRange(
            state=track_view_state,
            videos_metadata=videos_metadata,
            enable_filter_track_by_date=enable_filter_track_by_date,
        )
        previous_frame = SwitchToPrevious(
            track_view_state, videos_metadata, create_default_filter
        )
        next_frame = SwitchToNext(
            track_view_state, videos_metadata, create_default_filter
        )
        switch_event = SwitchToEvent(
            event_repository=event_repository,
            track_view_state=track_view_state,
            section_state=section_state,
            create_default_filter=create_default_filter,
        )
        get_sections = GetAllSections(section_repository)
        get_flows = GetAllFlows(flow_repository)
        save_otflow = SaveOtflow(flow_parser, get_sections, get_flows, file_state)
        config_parser = self.create_config_parser(run_config, video_parser)
        save_otconfig = SaveOtconfig(datastore, config_parser, file_state)
        quick_save_configuration = QuickSaveConfiguration(
            file_state, save_otflow, save_otconfig
        )
        load_otconfig = LoadOtconfig(
            clear_repositories,
            config_parser,
            project_updater,
            AddAllVideos(video_repository),
            AddAllSections(add_section),
            AddAllFlows(add_flow),
            load_track_files,
            remark_repository,
            parse_json,
        )
        get_all_videos = GetAllVideos(video_repository)
        get_current_project = GetCurrentProject(datastore)
        config_has_changed = ConfigHasChanged(
            OtconfigHasChanged(
                config_parser,
                get_sections,
                get_flows,
                get_current_project,
                get_all_videos,
                get_all_track_files,
            ),
            OtflowHasChanged(flow_parser, get_sections, get_flows),
            file_state,
        )
        export_road_user_assignments = self.create_export_road_user_assignments(
            get_all_tracks,
            section_repository,
            event_repository,
            flow_repository,
            create_events,
        )
        save_path_suggester = SavePathSuggester(
            file_state, get_all_track_files, get_all_videos, get_current_project
        )
        tracks_intersecting_sections = self._create_tracks_intersecting_sections(
            get_all_tracks
        )

        calculate_track_statistics = self._create_calculate_track_statistics(
            get_sections,
            tracks_intersecting_sections,
            get_sections_by_id,
            intersection_repository,
            road_user_assigner,
            event_repository,
            flow_repository,
            track_repository,
            section_repository,
            get_all_tracks,
        )
        get_road_user_assignments = GetRoadUserAssignments(
            flow_repository, event_repository, road_user_assigner
        )
        number_of_tracks_assigned_to_each_flow = NumberOfTracksAssignedToEachFlow(
            get_road_user_assignments, flow_repository
        )
        track_statistics_export_factory = SimpleTrackStatisticsExporterFactory()
        export_track_statistics = ExportTrackStatistics(
            calculate_track_statistics, track_statistics_export_factory
        )
        application = OTAnalyticsApplication(
            datastore,
            track_state,
            track_view_state,
            section_state,
            flow_state,
            file_state,
            tracks_metadata,
            videos_metadata,
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
        )
        section_repository.register_sections_observer(cut_tracks_intersecting_section)
        section_repository.register_section_changed_observer(
            cut_tracks_intersecting_section.notify_section_changed
        )
        cut_tracks_intersecting_section.register(clear_all_events.on_tracks_cut)
        application.connect_clear_event_repository_observer()
        name_generator = ArrowFlowNameGenerator()
        dummy_viewmodel = DummyViewModel(
            application,
            flow_parser,
            name_generator,
            event_list_export_formats=AVAILABLE_EVENTLIST_EXPORTERS,
            show_svz=run_config.show_svz,
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
        track_view_state.filter_date_active.register(
            dummy_viewmodel.change_filter_date_active
        )
        track_view_state.filter_element.register(
            selected_video_updater.on_filter_element_change
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
        event_repository.register_observer(dummy_viewmodel.update_track_statistics)
        load_otflow.register(file_state.last_saved_config.set)
        load_otconfig.register(file_state.last_saved_config.set)
        project_updater.register(dummy_viewmodel.update_quick_save_button)
        track_file_repository.register(dummy_viewmodel.update_quick_save_button)
        project_updater.register(dummy_viewmodel.show_current_project)
        project_updater.register(dummy_viewmodel.update_svz_metadata_view)

        for group in layer_groups:
            group.register(image_updater.notify_layers)
        main_window = ModifiedCTk(dummy_viewmodel)
        pulling_progressbar_popup_builder.add_widget(main_window)
        apply_cli_cuts = self.create_apply_cli_cuts(
            cut_tracks_intersecting_section, track_repository
        )
        preload_input_files = self.create_preload_input_files(
            load_otconfig=load_otconfig,
            load_otflow=load_otflow,
            load_track_files=load_track_files,
            apply_cli_cuts=apply_cli_cuts,
        )
        OTAnalyticsGui(
            main_window, dummy_viewmodel, layer_groups, preload_input_files, run_config
        ).start()

    def start_cli(self, run_config: RunConfiguration) -> None:
        track_repository = self._create_track_repository(run_config)
        section_repository = self._create_section_repository()
        flow_repository = self._create_flow_repository()

        event_repository = self._create_event_repository()
        add_section = AddSection(section_repository)
        get_sections_by_id = GetSectionsById(section_repository)
        get_all_sections = GetAllSections(section_repository)
        add_flow = AddFlow(flow_repository)
        add_events = AddEvents(event_repository)
        get_tracks_without_single_detections = GetTracksWithoutSingleDetections(
            track_repository
        )
        get_all_tracks = GetAllTracks(track_repository)
        get_all_track_ids = GetAllTrackIds(track_repository)
        clear_all_events = ClearAllEvents(event_repository)
        tracks_metadata = self._create_tracks_metadata(track_repository, run_config)
        videos_metadata = VideosMetadata()
        section_provider = FilterOutCuttingSections(section_repository.get_all)
        create_events = self._create_use_case_create_events(
            section_provider,
            clear_all_events,
            get_all_tracks,
            get_tracks_without_single_detections,
            add_events,
            run_config.num_processes,
        )
        cut_tracks = self._create_cut_tracks_intersecting_section(
            GetSectionsById(section_repository),
            get_all_tracks,
            AddAllTracks(track_repository),
            RemoveTracks(track_repository),
            RemoveSection(section_repository),
        )
        apply_cli_cuts = self.create_apply_cli_cuts(cut_tracks, track_repository)
        add_all_tracks = AddAllTracks(track_repository)
        clear_all_tracks = ClearAllTracks(track_repository)
        export_counts = self._create_export_counts(
            event_repository,
            flow_repository,
            get_sections_by_id,
            create_events,
        )
        tracks_metadata = self._create_tracks_metadata(track_repository, run_config)
        videos_metadata = VideosMetadata()
        export_tracks = CsvTrackExport(
            track_repository, tracks_metadata, videos_metadata
        )
        export_road_user_assignments = self.create_export_road_user_assignments(
            get_all_tracks,
            section_repository,
            event_repository,
            flow_repository,
            create_events,
        )

        cli: OTAnalyticsCli
        if run_config.cli_bulk_mode:
            track_parser = self._create_track_parser(track_repository)

            cli = OTAnalyticsBulkCli(
                run_config,
                event_repository,
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
                videos_metadata,
                export_tracks,
                export_road_user_assignments,
                track_parser,
                progressbar=TqdmBuilder(),
            )

        else:
            stream_track_parser = self._create_stream_track_parser(run_config)
            cli = OTAnalyticsStreamCli(
                run_config,
                event_repository,
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
                videos_metadata,
                export_tracks,
                export_road_user_assignments,
                stream_track_parser,
            )

        cli.start()

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
        remark_repository: RemarkRepository,
    ) -> Datastore:
        """
        Build all required objects and inject them where necessary

        Args:
            track_repository (TrackRepository): the track repository to inject
            progressbar_builder (ProgressbarBuilder): the progressbar builder to inject
        """
        track_parser = self._create_track_parser(track_repository)
        event_list_parser = self._create_event_list_parser()
        track_video_parser = OttrkVideoParser(video_parser)
        return Datastore(
            track_repository,
            track_file_repository,
            track_parser,
            section_repository,
            flow_repository,
            event_repository,
            event_list_parser,
            track_to_video_repository,
            video_repository,
            video_parser,
            track_video_parser,
            progressbar_builder,
            remark_repository,
        )

    def _create_track_repository(self, run_config: RunConfiguration) -> TrackRepository:
        return TrackRepository(
            FilteredPandasTrackDataset(
                PandasTrackDataset.from_list(
                    [], PygeosTrackGeometryDataset.from_track_dataset
                ),
                run_config.include_classes,
                run_config.exclude_classes,
            )
        )
        # return TrackRepository(PythonTrackDataset())

    def _create_track_parser(self, track_repository: TrackRepository) -> TrackParser:
        calculator = PandasByMaxConfidence()
        detection_parser = PandasDetectionParser(
            calculator,
            PygeosTrackGeometryDataset.from_track_dataset,
            track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT,
        )
        # calculator = ByMaxConfidence()
        # detection_parser = PythonDetectionParser(
        # noqa   calculator, track_repository, track_length_limit=DEFAULT_TRACK_LENGTH_LIMIT
        # )
        return OttrkParser(detection_parser)

    def _create_stream_track_parser(
        self, run_config: RunConfiguration
    ) -> StreamTrackParser:
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
            chunk_size=run_config.cli_chunk_size,
        )

    def _create_section_repository(self) -> SectionRepository:
        return SectionRepository()

    def _create_flow_parser(self) -> FlowParser:
        return OtFlowParser()

    def _create_flow_repository(self) -> FlowRepository:
        return FlowRepository()

    def _create_intersection_repository(self) -> IntersectionRepository:
        return PythonIntersectionRepository()

    def _create_event_repository(self) -> EventRepository:
        return EventRepository()

    def _create_event_list_parser(self) -> EventListParser:
        return OtEventListParser()

    def _create_track_state(self) -> TrackState:
        return TrackState()

    def _create_track_view_state(self) -> TrackViewState:
        return TrackViewState()

    def _create_layers(
        self,
        datastore: Datastore,
        intersection_repository: IntersectionRepository,
        track_view_state: TrackViewState,
        videos_metadata: VideosMetadata,
        flow_state: FlowState,
        section_state: SectionState,
        pulling_progressbar_builder: ProgressbarBuilder,
        road_user_assigner: RoadUserAssigner,
        color_palette_provider: ColorPaletteProvider,
    ) -> tuple[Sequence[LayerGroup], Sequence[PlottingLayer]]:
        return VisualizationBuilder(
            datastore,
            intersection_repository,
            track_view_state,
            videos_metadata,
            section_state,
            color_palette_provider,
            pulling_progressbar_builder,
        ).build(
            flow_state,
            road_user_assigner,
        )

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
        self, section_provider: SectionProvider, flow_repository: FlowRepository
    ) -> GenerateFlows:
        id_generator: FlowIdGenerator = RepositoryFlowIdGenerator(flow_repository)
        name_generator = ArrowFlowNameGenerator()
        flow_generator = CrossProductFlowGenerator(
            id_generator=id_generator,
            name_generator=name_generator,
            predicate=FilterSameSection().and_then(FilterExisting(flow_repository)),
        )
        return GenerateFlows(
            section_provider=section_provider,
            flow_repository=flow_repository,
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

    def _create_tracks_metadata(
        self, track_repository: TrackRepository, run_config: RunConfiguration
    ) -> TracksMetadata:
        return TracksMetadata(
            track_repository, run_config.include_classes, run_config.exclude_classes
        )

    def _create_action_state(self) -> ActionState:
        return ActionState()

    def _create_filter_element_setting_restorer(self) -> FilterElementSettingRestorer:
        return FilterElementSettingRestorer()

    @staticmethod
    def _create_export_counts(
        event_repository: EventRepository,
        flow_repository: FlowRepository,
        get_sections_by_id: GetSectionsById,
        create_events: CreateEvents,
    ) -> ExportCounts:
        return ExportTrafficCounting(
            event_repository,
            flow_repository,
            get_sections_by_id,
            create_events,
            FilterBySectionEnterEvent(SimpleRoadUserAssigner()),
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
            parse_json,
        )

    @staticmethod
    def _create_use_case_clear_all_repositories(
        clear_all_events: ClearAllEvents,
        clear_all_flows: ClearAllFlows,
        clear_all_intersections: ClearAllIntersections,
        clear_all_sections: ClearAllSections,
        clear_all_track_to_videos: ClearAllTrackToVideos,
        clear_all_tracks: ClearAllTracks,
        clear_all_videos: ClearAllVideos,
    ) -> ClearRepositories:
        return ClearRepositories(
            clear_all_events,
            clear_all_flows,
            clear_all_intersections,
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
        file_state: FileState,
    ) -> StartNewProject:
        return StartNewProject(
            clear_repositories, reset_project_config, track_view_state, file_state
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
        self,
        video_parser: VideoParser,
        track_repository: TrackRepository,
        track_file_repository: TrackFileRepository,
        video_repository: VideoRepository,
        track_to_video_repository: TrackToVideoRepository,
        progressbar: ProgressbarBuilder,
        tracks_metadata: TracksMetadata,
        videos_metadata: VideosMetadata,
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
            videos_metadata,
        )

    def _create_video_parser(self, videos_metadata: VideosMetadata) -> VideoParser:
        return CachedVideoParser(SimpleVideoParser(PyAvVideoReader(videos_metadata)))

    def _create_remark_repository(self) -> RemarkRepository:
        return RemarkRepository()

    def _create_video_repository(self) -> VideoRepository:
        return VideoRepository()

    def _create_track_to_video_repository(self) -> TrackToVideoRepository:
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
        self,
        cut_tracks: CutTracksIntersectingSection,
        track_repository: TrackRepository,
    ) -> ApplyCliCuts:
        return ApplyCliCuts(cut_tracks, TrackRepositorySize(track_repository))

    def create_config_parser(
        self,
        run_config: RunConfiguration,
        video_parser: VideoParser,
    ) -> OtConfigParser:
        flow_parser = self._create_flow_parser()
        format_fixer = self._create_format_fixer(run_config)
        return OtConfigParser(
            video_parser=video_parser,
            flow_parser=flow_parser,
            format_fixer=format_fixer,
        )

    def create_export_road_user_assignments(
        self,
        get_all_tracks: GetAllTracks,
        section_repository: SectionRepository,
        event_repository: EventRepository,
        flow_repository: FlowRepository,
        create_events: CreateEvents,
    ) -> ExportRoadUserAssignments:
        return ExportRoadUserAssignments(
            event_repository,
            flow_repository,
            create_events,
            FilterBySectionEnterEvent(SimpleRoadUserAssigner()),
            SimpleRoadUserAssignmentExporterFactory(section_repository, get_all_tracks),
        )

    def _create_calculate_track_statistics(
        self,
        get_all_sections: GetAllSections,
        tracks_intersecting_sections: TracksIntersectingSections,
        get_section_by_id: GetSectionsById,
        intersection_repository: IntersectionRepository,
        road_user_assigner: RoadUserAssigner,
        event_repository: EventRepository,
        flow_repository: FlowRepository,
        track_repository: TrackRepository,
        section_repository: SectionRepository,
        get_all_tracks: GetAllTracks,
    ) -> CalculateTrackStatistics:
        get_cutting_sections = GetCuttingSections(section_repository)
        tracks_intersecting_all_sections = TracksIntersectingAllNonCuttingSections(
            get_cutting_sections,
            get_all_sections,
            tracks_intersecting_sections,
            get_section_by_id,
            intersection_repository,
        )
        tracks_assigned_to_all_flows = TracksAssignedToAllFlows(
            road_user_assigner, event_repository, flow_repository
        )
        track_ids_inside_cutting_sections = TrackIdsInsideCuttingSections(
            get_all_tracks, get_cutting_sections
        )
        get_all_track_ids = GetAllTrackIds(track_repository)
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
        get_events = GetAllEnterSectionEvents(event_repository=event_repository)
        return CalculateTrackStatistics(
            tracks_intersecting_all_sections,
            tracks_assigned_to_all_flows,
            get_all_track_ids,
            track_ids_inside_cutting_sections,
            number_of_tracks_to_be_validated,
            get_events,
        )
