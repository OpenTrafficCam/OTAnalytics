from abc import ABC, abstractmethod
from functools import cached_property
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
    TrafficCounting,
)
from OTAnalytics.application.analysis.traffic_counting_specification import ExportCounts
from OTAnalytics.application.config_specification import OtConfigDefaultValueProvider
from OTAnalytics.application.datastore import (
    Datastore,
    EventListParser,
    TrackParser,
    TrackToVideoRepository,
    VideoParser,
)
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.parser.flow_parser import FlowParser
from OTAnalytics.application.plotting import LayeredPlotter, LayerGroup, PlottingLayer
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.application.run_configuration import (
    RunConfiguration,
    RunConfigurationError,
)
from OTAnalytics.application.state import (
    ActionState,
    FileState,
    FlowState,
    SectionState,
    SelectedVideoUpdate,
    TrackImageSizeUpdater,
    TrackImageUpdater,
    TracksMetadata,
    TrackState,
    TrackViewState,
    VideoImageSizeUpdater,
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
    FilterOutCuttingSections,
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
from OTAnalytics.application.use_cases.editor.section_editor import (
    AddNewSection,
    CreateSectionId,
    UpdateSectionCoordinates,
)
from OTAnalytics.application.use_cases.event_repository import (
    AddEvents,
    ClearAllEvents,
    GetAllEnterSectionEvents,
    RemoveEventsByRoadUserId,
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
    CachedTrackIdsInsideCuttingSections,
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
    FilteredTrackIdProviderByTrackIdProvider,
    GetAllTrackFiles,
    GetAllTrackIds,
    GetAllTracks,
    GetTracksWithoutSingleDetections,
    RemoveTracks,
    RemoveTracksByOriginalIds,
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
from OTAnalytics.application.use_cases.update_count_plots import (
    CountPlotSaver,
    CountPlotsUpdater,
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
from OTAnalytics.domain.track import TrackIdProvider
from OTAnalytics.domain.track_dataset.track_dataset import TRACK_GEOMETRY_FACTORY
from OTAnalytics.domain.track_repository import TrackFileRepository, TrackRepository
from OTAnalytics.domain.video import VideoRepository
from OTAnalytics.plugin_datastore.pandas_track_dataset_factory import (
    PandasTrackDatasetFactory,
    TypeCheckingPandasTrackDatasetFactory,
)
from OTAnalytics.plugin_datastore.python_track_store import ByMaxConfidence
from OTAnalytics.plugin_datastore.track_geometry_store.shapely_store import (
    ShapelyTrackGeometryDataset,
)
from OTAnalytics.plugin_datastore.track_store import (
    FilterByClassPandasTrackDataset,
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
from OTAnalytics.plugin_ui.intersection_repository import PythonIntersectionRepository
from OTAnalytics.plugin_ui.visualization.counts.counts_plotter import (
    ClassByFlowCountPlotter,
    CountPlotter,
    FlowByClassCountPlotter,
    MatplotlibCountBarPlotStyler,
    MatplotlibCountLinePlotStyler,
    MultipleCountPlotters,
)
from OTAnalytics.plugin_ui.visualization.visualization import VisualizationBuilder
from OTAnalytics.plugin_video_processing.video_reader import PyAvVideoReader

DETECTION_RATE_PERCENTILE_VALUE = 0.9


class BaseOtAnalyticsApplicationStarter(ABC):
    @abstractmethod
    @cached_property
    def create_events(self) -> CreateEvents:
        raise NotImplementedError

    @abstractmethod
    @cached_property
    def all_filtered_track_ids(self) -> TrackIdProvider:
        raise NotImplementedError

    @abstractmethod
    def start(self) -> None:
        raise NotImplementedError

    def __init__(self, run_config: RunConfiguration) -> None:
        self.run_config = run_config

    @cached_property
    def layered_plotter(self) -> LayeredPlotter:
        layer_groups, layers = self.layers
        return LayeredPlotter(layers=layers)

    @cached_property
    def flow_name_generator(self) -> FlowNameGenerator:
        return ArrowFlowNameGenerator()

    @cached_property
    def export_track_statistics(self) -> ExportTrackStatistics:
        return ExportTrackStatistics(
            self.calculate_track_statistics,
            self.track_statistics_exporter_factory,
        )

    @cached_property
    def track_statistics_exporter_factory(self) -> TrackStatisticsExporterFactory:
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

    @cached_property
    def track_image_updater(self) -> TrackImageUpdater:
        return TrackImageUpdater(
            self.datastore,
            self.track_view_state,
            self.section_state,
            self.flow_state,
            self.layered_plotter,
        )

    @cached_property
    def video_image_size_updater(self) -> VideoImageSizeUpdater:
        return VideoImageSizeUpdater(self.track_image_size_updater)

    @cached_property
    def track_image_size_updater(self) -> TrackImageSizeUpdater:
        return TrackImageSizeUpdater(self.track_view_state)

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

    @property
    @abstractmethod
    def progressbar_builder(self) -> ProgressbarBuilder:
        raise NotImplementedError

    @cached_property
    def videos_metadata(self) -> VideosMetadata:
        return create_videos_metadata()

    @cached_property
    def csv_track_export(self) -> CsvTrackExport:
        return CsvTrackExport(
            self.track_repository, self.tracks_metadata, self.videos_metadata
        )

    @cached_property
    def get_all_track_ids(self) -> GetAllTrackIds:
        return GetAllTrackIds(self.track_repository)

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
            self.progressbar_builder,
            self.remark_repository,
        )

    @cached_property
    def track_repository(self) -> TrackRepository:
        return TrackRepository(
            FilterByClassPandasTrackDataset(
                PandasTrackDataset.from_list(
                    [],
                    self.track_geometry_factory,
                    self.pandas_by_max_confidence,
                ),
                self.run_config.include_classes,
                self.run_config.exclude_classes,
            )
        )

    def _create_track_parser(self) -> TrackParser:
        detection_parser = PandasDetectionParser(
            self.pandas_by_max_confidence,
            self.track_geometry_factory,
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
                self.track_geometry_factory,
                self.pandas_by_max_confidence,
            ),
            chunk_size=self.run_config.cli_chunk_size,
        )

    @cached_property
    def section_repository(self) -> SectionRepository:
        return SectionRepository()

    @cached_property
    def flow_parser(self) -> FlowParser:
        return create_otflow_parser()

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

    @cached_property
    def visualization_builder(
        self,
    ) -> VisualizationBuilder:
        return VisualizationBuilder(
            self.datastore,
            self.intersection_repository,
            self.track_view_state,
            self.videos_metadata,
            self.section_state,
            self.color_palette_provider,
            self.progressbar_builder,
        )

    @cached_property
    def layers(self) -> tuple[Sequence[LayerGroup], Sequence[PlottingLayer]]:
        return self.visualization_builder.build(
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
            name_generator=self.flow_name_generator,
            predicate=FilterSameSection().and_then(
                FilterExisting(self.flow_repository)
            ),
        )
        return GenerateFlows(
            section_provider=section_provider,
            flow_repository=self.flow_repository,
            flow_generator=flow_generator,
        )

    @cached_property
    def intersect(self) -> RunIntersect:
        return BatchedTracksRunIntersect(
            intersect_parallelizer=MultiprocessingIntersectParallelization(
                self.run_config.num_processes
            ),
            get_tracks=self.get_all_tracks,
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

    @cached_property
    def export_counts(self) -> ExportCounts:
        return ExportTrafficCounting(
            self.traffic_counting,
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
    ) -> CreateEvents:
        create_intersection_events = SimpleCreateIntersectionEvents(
            self.intersect, section_provider, self.add_events
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
            self.progressbar_builder,
            self.tracks_metadata,
            self.videos_metadata,
        )

    @cached_property
    def video_parser(self) -> VideoParser:
        return create_video_parser(self.videos_metadata)

    @cached_property
    def remark_repository(self) -> RemarkRepository:
        return RemarkRepository()

    @cached_property
    def video_repository(self) -> VideoRepository:
        return VideoRepository()

    @cached_property
    def track_to_video_repository(self) -> TrackToVideoRepository:
        return TrackToVideoRepository()

    @cached_property
    def preload_input_files(self) -> PreloadInputFiles:
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
        format_fixer = create_format_fixer(self.run_config)
        return OtConfigParser(
            video_parser=self.video_parser,
            flow_parser=self.flow_parser,
            format_fixer=format_fixer,
        )

    @cached_property
    def export_road_user_assignments(self) -> ExportRoadUserAssignments:
        return ExportRoadUserAssignments(
            self.event_repository,
            self.flow_repository,
            self.create_events,
            self.road_user_assigner,
            SimpleRoadUserAssignmentExporterFactory(
                self.section_repository, self.get_all_tracks
            ),
        )

    @cached_property
    def calculate_track_statistics(self) -> CalculateTrackStatistics:
        tracks_intersecting_all_sections = FilteredTrackIdProviderByTrackIdProvider(
            TracksIntersectingAllNonCuttingSections(
                self.get_cutting_sections,
                self.get_all_sections,
                self.tracks_intersecting_sections,
                self.get_sections_by_id,
                self.intersection_repository,
            ),
            self.all_filtered_track_ids,
        )
        tracks_assigned_to_all_flows = FilteredTrackIdProviderByTrackIdProvider(
            TracksAssignedToAllFlows(
                self.road_user_assigner, self.event_repository, self.flow_repository
            ),
            self.all_filtered_track_ids,
        )
        track_ids_inside_cutting_sections = FilteredTrackIdProviderByTrackIdProvider(
            self._create_cached_track_ids_inside_cutting_sections(
                self.get_all_tracks,
                self.get_cutting_sections,
                self.track_repository,
                self.section_repository,
            ),
            self.all_filtered_track_ids,
        )
        tracks_as_dataframe_provider = TracksAsDataFrameProvider(
            get_all_tracks=self.get_all_tracks,
            track_geometry_factory=self.track_geometry_factory,
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
            self.all_filtered_track_ids,
            track_ids_inside_cutting_sections,
            number_of_tracks_to_be_validated,
            get_events,
        )

    def _create_cached_track_ids_inside_cutting_sections(
        self,
        get_all_tracks: GetAllTracks,
        get_cutting_sections: GetCuttingSections,
        track_repository: TrackRepository,
        section_repository: SectionRepository,
    ) -> CachedTrackIdsInsideCuttingSections:
        cached = CachedTrackIdsInsideCuttingSections(
            get_all_tracks, get_cutting_sections
        )
        track_repository.register_tracks_observer(cached)
        section_repository.register_sections_observer(cached)
        return cached

    @cached_property
    def get_cutting_sections(self) -> GetCuttingSections:
        return GetCuttingSections(self.section_repository)

    @cached_property
    def create_section_id(self) -> CreateSectionId:
        return CreateSectionId(self.section_repository)

    @cached_property
    def add_new_section(self) -> AddNewSection:
        return AddNewSection(
            create_section_id=self.create_section_id,
            add_section=self.add_section,
        )

    @cached_property
    def update_section_coordinates(self) -> UpdateSectionCoordinates:
        return UpdateSectionCoordinates(self.section_repository)

    @cached_property
    def resource_manager(self) -> ResourceManager:
        return ResourceManager()

    @cached_property
    def pandas_track_dataset_factory(self) -> PandasTrackDatasetFactory:
        return TypeCheckingPandasTrackDatasetFactory(
            self.track_geometry_factory, self.pandas_by_max_confidence
        )

    @cached_property
    def pandas_by_max_confidence(self) -> PandasByMaxConfidence:
        return PandasByMaxConfidence()

    @cached_property
    def track_geometry_factory(self) -> TRACK_GEOMETRY_FACTORY:
        return ShapelyTrackGeometryDataset.from_track_dataset

    @cached_property
    def remove_events_by_road_user_id(self) -> RemoveEventsByRoadUserId:
        return RemoveEventsByRoadUserId(self.event_repository)

    @cached_property
    def remove_tracks_by_original_ids(self) -> RemoveTracksByOriginalIds:
        return RemoveTracksByOriginalIds(self.track_repository)

    @cached_property
    def traffic_counting(self) -> TrafficCounting:
        return TrafficCounting(
            self.event_repository,
            self.flow_repository,
            self.get_sections_by_id,
            self.create_events,
            self.road_user_assigner,
            SimpleTaggerFactory(),
        )

    @cached_property
    def update_count_plots(self) -> CountPlotsUpdater:
        return CountPlotsUpdater(self.track_view_state, self.count_plotter)

    @cached_property
    def save_count_plots(self) -> CountPlotSaver:
        try:
            save_dir = self.run_config.save_dir
        except RunConfigurationError:
            save_dir = Path.cwd()

        return CountPlotSaver(path=save_dir / "results")

    @cached_property
    def count_plotter(self) -> CountPlotter:
        return MultipleCountPlotters(
            self.traffic_counting,
            plotters=[
                FlowByClassCountPlotter(
                    self.traffic_counting,
                    self.color_palette_provider,
                    self.tracks_metadata,
                    interval_in_minutes=5,  # TODO configure interval
                    styler=MatplotlibCountLinePlotStyler(legend=True),
                ),
                ClassByFlowCountPlotter(
                    self.traffic_counting,
                    self.color_palette_provider,
                    self.tracks_metadata,
                    interval_in_minutes=5,  # TODO configure interval
                    styler=MatplotlibCountLinePlotStyler(legend=True),
                ),
                FlowByClassCountPlotter(
                    self.traffic_counting,
                    self.color_palette_provider,
                    self.tracks_metadata,
                    interval_in_minutes=5,  # TODO configure interval
                    styler=MatplotlibCountBarPlotStyler(
                        legend=True, time_interval_min=5
                    ),
                ),
                ClassByFlowCountPlotter(
                    self.traffic_counting,
                    self.color_palette_provider,
                    self.tracks_metadata,
                    interval_in_minutes=5,  # TODO configure interval
                    styler=MatplotlibCountBarPlotStyler(
                        legend=True, ascending_trace_sum=True, time_interval_min=5
                    ),
                ),
            ],
        )


def create_format_fixer(
    default_value_provider: OtConfigDefaultValueProvider,
) -> OtConfigFormatFixer:
    return MultiFixer([FixMissingAnalysis(default_value_provider)])


def create_video_parser(videos_metadata: VideosMetadata) -> VideoParser:
    return CachedVideoParser(SimpleVideoParser(PyAvVideoReader(videos_metadata)))


def create_videos_metadata() -> VideosMetadata:
    return VideosMetadata()


def create_otflow_parser() -> OtFlowParser:
    return OtFlowParser()
