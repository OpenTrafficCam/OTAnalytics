from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
    ExportCounts,
    ExportFormat,
)
from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.project import SvzMetadata
from OTAnalytics.application.state import (
    ActionState,
    FileState,
    FlowState,
    SectionState,
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
from OTAnalytics.application.use_cases.config import SaveOtconfig
from OTAnalytics.application.use_cases.config_has_changed import ConfigHasChanged
from OTAnalytics.application.use_cases.create_events import (
    CreateEvents,
    CreateIntersectionEvents,
)
from OTAnalytics.application.use_cases.event_repository import ClearAllEvents
from OTAnalytics.application.use_cases.export_events import EventListExporter
from OTAnalytics.application.use_cases.filter_visualization import (
    EnableFilterTrackByDate,
)
from OTAnalytics.application.use_cases.flow_repository import AddFlow
from OTAnalytics.application.use_cases.flow_statistics import (
    NumberOfTracksAssignedToEachFlow,
)
from OTAnalytics.application.use_cases.generate_flows import GenerateFlows
from OTAnalytics.application.use_cases.get_current_remark import GetCurrentRemark
from OTAnalytics.application.use_cases.load_otconfig import LoadOtconfig
from OTAnalytics.application.use_cases.load_otflow import LoadOtflow
from OTAnalytics.application.use_cases.load_track_files import LoadTrackFiles
from OTAnalytics.application.use_cases.quick_save_configuration import (
    QuickSaveConfiguration,
)
from OTAnalytics.application.use_cases.road_user_assignment_export import (
    ExportRoadUserAssignments,
    ExportSpecification,
)
from OTAnalytics.application.use_cases.save_otflow import SaveOtflow
from OTAnalytics.application.use_cases.section_repository import (
    AddSection,
    GetSectionOffset,
    GetSectionsById,
)
from OTAnalytics.application.use_cases.start_new_project import StartNewProject
from OTAnalytics.application.use_cases.suggest_save_path import SavePathSuggester
from OTAnalytics.application.use_cases.track_repository import (
    GetAllTrackFiles,
    TrackRepositorySize,
)
from OTAnalytics.application.use_cases.track_statistics import (
    CalculateTrackStatistics,
    TrackStatistics,
)
from OTAnalytics.application.use_cases.track_statistics_export import (
    ExportTrackStatistics,
    TrackStatisticsExportSpecification,
)
from OTAnalytics.application.use_cases.update_count_plots import CountPlotsUpdater
from OTAnalytics.application.use_cases.update_project import ProjectUpdater
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import FilterElement, FilterElementSettingRestorer
from OTAnalytics.domain.flow import Flow, FlowChangedObserver, FlowId, FlowListObserver
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import (
    Section,
    SectionChangedObserver,
    SectionId,
    SectionListObserver,
)
from OTAnalytics.domain.track import TrackId, TrackImage
from OTAnalytics.domain.types import EventType
from OTAnalytics.domain.video import Video, VideoListObserver


class CancelAddSection(Exception):
    pass


class CancelAddFlow(Exception):
    pass


class MultipleSectionsSelected(Exception):
    pass


class MultipleFlowsSelected(Exception):
    pass


class OTAnalyticsApplication:
    """
    Entrypoint for calls from the UI.
    """

    def __init__(
        self,
        datastore: Datastore,
        track_state: TrackState,
        track_view_state: TrackViewState,
        section_state: SectionState,
        flow_state: FlowState,
        file_state: FileState,
        tracks_metadata: TracksMetadata,
        videos_metadata: VideosMetadata,
        action_state: ActionState,
        filter_element_setting_restorer: FilterElementSettingRestorer,
        get_all_track_files: GetAllTrackFiles,
        generate_flows: GenerateFlows,
        create_intersection_events: CreateIntersectionEvents,
        export_counts: ExportCounts,
        create_events: CreateEvents,
        load_otflow: LoadOtflow,
        add_section: AddSection,
        add_flow: AddFlow,
        clear_all_events: ClearAllEvents,
        start_new_project: StartNewProject,
        project_updater: ProjectUpdater,
        save_otconfig: SaveOtconfig,
        load_track_files: LoadTrackFiles,
        enable_filter_by_date: EnableFilterTrackByDate,
        previous_frame: SwitchToPrevious,
        next_frame: SwitchToNext,
        switch_event: SwitchToEvent,
        save_otflow: SaveOtflow,
        quick_save_configuration: QuickSaveConfiguration,
        load_otconfig: LoadOtconfig,
        config_has_changed: ConfigHasChanged,
        export_road_user_assignments: ExportRoadUserAssignments,
        file_name_suggester: SavePathSuggester,
        calculate_track_statistics: CalculateTrackStatistics,
        number_of_tracks_assigned_to_each_flow: NumberOfTracksAssignedToEachFlow,
        export_track_statistics: ExportTrackStatistics,
        get_current_remark: GetCurrentRemark,
        update_count_plots: CountPlotsUpdater,
    ) -> None:
        self._datastore: Datastore = datastore
        self.track_state: TrackState = track_state
        self.track_view_state: TrackViewState = track_view_state
        self.section_state: SectionState = section_state
        self.flow_state: FlowState = flow_state
        self.file_state = file_state
        self._tracks_metadata = tracks_metadata
        self._videos_metadata = videos_metadata
        self.action_state = action_state
        self._filter_element_setting_restorer = filter_element_setting_restorer
        self._add_section = add_section
        self._add_flow = add_flow
        self._get_all_track_files = get_all_track_files
        self._generate_flows = generate_flows
        self._create_intersection_events = create_intersection_events
        self._clear_all_events = clear_all_events
        self._export_counts = export_counts
        self._project_updater = project_updater
        self._save_otconfig = save_otconfig
        self._create_events = create_events
        self._load_otflow = load_otflow
        self._start_new_project = start_new_project
        self._load_track_files = load_track_files
        self._get_section_offset = GetSectionOffset(
            GetSectionsById(self._datastore._section_repository)
        )
        self._track_repository_size = TrackRepositorySize(
            self._datastore._track_repository
        )
        self._enable_filter_by_date = enable_filter_by_date
        self._switch_previous = previous_frame
        self._switch_next = next_frame
        self._switch_event = switch_event
        self._save_otflow = save_otflow
        self._quick_save_configuration = quick_save_configuration
        self._load_otconfig = load_otconfig
        self._config_has_changed = config_has_changed
        self._export_road_user_assignments = export_road_user_assignments
        self._file_name_suggester = file_name_suggester
        self._calculate_track_statistics = calculate_track_statistics
        self._number_of_tracks_assigned_to_each_flow = (
            number_of_tracks_assigned_to_each_flow
        )
        self._export_track_statistics = export_track_statistics
        self._get_current_remark = get_current_remark
        self._update_count_plots = update_count_plots

    def connect_observers(self) -> None:
        """
        Connect the observers with the repositories to listen to domain object changes.
        """
        self._datastore.register_tracks_observer(self.track_state)
        self._datastore.register_tracks_observer(self._tracks_metadata)
        self._datastore.register_sections_observer(self.section_state)

    def connect_clear_event_repository_observer(self) -> None:
        self._datastore.register_sections_observer(self._clear_all_events)
        self._datastore.register_section_changed_observer(
            self._clear_all_events.on_section_changed
        )
        self._datastore.register_tracks_observer(self._clear_all_events)

    def register_video_observer(self, observer: VideoListObserver) -> None:
        self._datastore.register_video_observer(observer)

    def register_sections_observer(self, observer: SectionListObserver) -> None:
        self._datastore.register_sections_observer(observer)

    def register_section_changed_observer(
        self, observer: SectionChangedObserver
    ) -> None:
        self._datastore.register_section_changed_observer(observer)

    def register_flows_observer(self, observer: FlowListObserver) -> None:
        self._datastore.register_flows_observer(observer)

    def register_flow_changed_observer(self, observer: FlowChangedObserver) -> None:
        self._datastore.register_flow_changed_observer(observer)

    def get_all_sections(self) -> list[Section]:
        return self._datastore.get_all_sections()

    def get_section_for(self, section_id: SectionId) -> Optional[Section]:
        return self._datastore.get_section_for(section_id)

    def add_videos(self, files: list[Path]) -> None:
        self._datastore.load_video_files(files)

    def remove_videos(self) -> None:
        """
        Remove the currently selected videos from the repository.
        """
        if videos := self.get_selected_videos():
            self._datastore.remove_videos(videos)
            if videos := self._datastore.get_all_videos():
                self.track_view_state.selected_videos.set([videos[0]])
            else:
                self.track_view_state.selected_videos.set([])

    def get_remark(self) -> str:
        return self._get_current_remark.get()

    def get_all_videos(self) -> list[Video]:
        return self._datastore.get_all_videos()

    def get_selected_videos(self) -> list[Video]:
        return self.track_view_state.selected_videos.get()

    def get_all_track_files(self) -> set[Path]:
        return self._get_all_track_files()

    def get_all_flows(self) -> list[Flow]:
        return self._datastore.get_all_flows()

    def get_flow_for(self, flow_id: FlowId) -> Optional[Flow]:
        return self._datastore.get_flow_for(flow_id)

    def get_flow_id(self) -> FlowId:
        """
        Get an id for a new flow
        """
        return self._datastore.get_flow_id()

    def is_flow_name_valid(self, flow_name: str) -> bool:
        """
        Check whether a flow with the given name already exists.

        Args:
            flow_name (str): name to check

        Returns:
            bool: True if a flow with the name already exists, False otherwise.
        """
        return self._add_flow.is_flow_name_valid(flow_name)

    def add_flow(self, flow: Flow) -> None:
        self._add_flow(flow)

    def generate_flows(self) -> None:
        self._generate_flows.generate()

    def remove_flow(self, flow_id: FlowId) -> None:
        self._datastore.remove_flow(flow_id)

    def update_flow(self, flow: Flow) -> None:
        self._datastore.update_flow(flow)

    def save_otconfig(self, file: Path) -> None:
        self._save_otconfig(file)

    def load_otconfig(self, file: Path) -> None:
        self._load_otconfig.load(file)

    def add_tracks_of_files(self, track_files: list[Path]) -> None:
        """
        Load a multiple track files.

        Args:
            track_files (list[Path]): files in ottrk format
        """
        self._load_track_files(track_files)

    def delete_all_tracks(self) -> None:
        """Delete all tracks."""
        self._datastore.delete_all_tracks()

    def load_otflow(self, sections_file: Path) -> None:
        """
        Load sections from a sections file.

        Args:
            sections_file (Path): file in sections format
        """
        self._load_otflow(sections_file)

    def is_flow_using_section(self, section: SectionId) -> bool:
        """
        Checks if the section id is used by flows.

        Args:
            section (SectionId): section to check

        Returns:
            bool: true if the section is used by at least one flow
        """
        return self._datastore.is_flow_using_section(section)

    def flows_using_section(self, section: SectionId) -> list[Flow]:
        """
        Returns a list of flows using the section as start or end.

        Args:
            section (SectionId): section to search flows for

        Returns:
            list[FlowId]: flows using the section
        """
        return self._datastore.flows_using_section(section)

    def get_section_id(self) -> SectionId:
        """
        Get an id for a new section
        """
        return self._datastore.get_section_id()

    def is_section_name_valid(self, section_name: str) -> bool:
        """
        Check whether a section with the given name already exists.

        Args:
            section_name (str): name to check

        Returns:
            bool: True if a section with the name already exists, False otherwise.
        """
        return self._add_section.is_section_name_valid(section_name)

    def add_section(self, section: Section) -> None:
        """
        Add a new section

        Args:
            section (Section): section to add
        """
        self._add_section(section)

    def remove_section(self, section: SectionId) -> None:
        """
        Remove the section

        Args:
            section (SectionId): section to remove
        """
        self._datastore.remove_section(section)

    def update_section(self, section: Section) -> None:
        """
        Update the section.

        Args:
            section (Section): updated section
        """
        self._datastore.update_section(section)

    def set_section_plugin_data(self, section_id: SectionId, plugin_data: dict) -> None:
        """
        Set the plugin data of the section. The data will be overridden.

        Args:
            section_id (SectionId): section id to override the plugin data at
            plugin_data (dict): value of the new plugin data
        """
        self._datastore.set_section_plugin_data(
            section_id=section_id, plugin_data=plugin_data
        )

    def save_otflow(self, file: Path) -> None:
        """
        Save the flows and sections from the repositories into a file.

        Args:
            file (Path): file to save the flows and sections to
        """
        self._save_otflow.save(file)

    def get_image_of_track(self, track_id: TrackId) -> Optional[TrackImage]:
        """
        Retrieve an image for the given track.

        Args:
            track_id (TrackId): identifier for the track

        Returns:
            Optional[TrackImage]: an image of the track if the track is available and
            the image can be loaded
        """
        return self._datastore.get_image_of_track(track_id)

    def create_events(self) -> None:
        """
        Intersect all tracks with all sections and write the events into the event
        repository
        """
        self._create_events()

    def intersect_tracks_with_sections(self) -> None:
        self._create_intersection_events()

    def save_events(self, file: Path) -> None:
        """
        Save the event repository into a file.

        Args:
            file (Path): file to save the events to
        """
        self._datastore.save_event_list_file(file)

    def export_events(self, file: Path, event_list_exporter: EventListExporter) -> None:
        """
        Export the event repository into other formats (like CSV or Excel)

        Args:
            file (Path): File to export the events to
            event_list_exporter (EventListExporter): Exporter building the format
        """
        if self._datastore._event_repository.is_empty():
            self.create_events()
        self._datastore.export_event_list_file(file, event_list_exporter)

    def get_supported_export_formats(self) -> Iterable[ExportFormat]:
        """
        Returns an iterable of the supported export formats.

        Returns:
            Iterable[ExportFormat]: supported export formats
        """
        return self._export_counts.get_supported_formats()

    def export_counts(self, specification: CountingSpecificationDto) -> None:
        """
        Export the traffic countings based on the currently available events and flows.

        Args:
            specification (CountingSpecificationDto): specification of the export
        """
        self._export_counts.export(specification)

    def change_track_offset_to_section_offset(
        self, event_type: EventType = EventType.SECTION_ENTER
    ) -> None:
        """
        Change the offset to visualize tracks to the offset of the currently selected
        section.

        Args:
            event_type (EventType, optional): event type of the offset at the section.
            Defaults to EventType.SECTION_ENTER.
        """
        if len(section_id := self.section_state.selected_sections.get()) == 1:
            if section := self._datastore.get_section_for(section_id[0]):
                if offset := section.relative_offset_coordinates.get(event_type):
                    self.track_view_state.track_offset.set(offset)

    def set_selected_section(self, ids: list[str]) -> None:
        """Set the current selected section in the UI.

        Args:
            id (Optional[str]): the id of the currently selected section
        """
        section_ids = [SectionId(id) for id in ids]
        self.section_state.selected_sections.set(section_ids)

    def set_selected_flows(self, ids: list[str]) -> None:
        """Set the current selected flow in the UI.

        Args:
            id (Optional[str]): the id of the currently selected flow
        """
        flow_ids = [FlowId(id) for id in ids]
        self.flow_state.selected_flows.set(flow_ids)

    def get_current_track_offset(self) -> Optional[RelativeOffsetCoordinate]:
        """Get the current track offset.

        Returns:
            Optional[RelativeOffsetCoordinate]: the current track offset.
        """
        return self.track_view_state.track_offset.get()

    def next_frame(self) -> None:
        self._switch_next.switch_frame()

    def previous_frame(self) -> None:
        self._switch_previous.switch_frame()

    def next_second(self) -> None:
        self._switch_next.switch_second()

    def previous_second(self) -> None:
        self._switch_previous.switch_second()

    def next_event(self) -> None:
        self._switch_event.switch_to_next()

    def previous_event(self) -> None:
        self._switch_event.switch_to_previous()

    def update_date_range_tracks_filter(self, date_range: DateRange) -> None:
        """Update the date range of the track filter.

        Args:
            date_range (DateRange): the date range
        """
        current_filter_element = self.track_view_state.filter_element.get()

        self.track_view_state.filter_element.set(
            current_filter_element.derive_date(date_range)
        )

    def update_class_tracks_filter(self, classifications: Optional[set[str]]) -> None:
        """Update the classifications of the track filter.

        Args:
            classifications (set[str]): the classifications
        """
        current_filter_element = self.track_view_state.filter_element.get()

        self.track_view_state.filter_element.set(
            current_filter_element.derive_classifications(classifications)
        )

    def enable_filter_track_by_date(self) -> None:
        """Enable filtering track by date and restoring the previous date range."""
        self._enable_filter_by_date.enable()

    def disable_filter_track_by_date(self) -> None:
        """Disable filtering track by date and saving the current date range."""
        current_filter_element = self.track_view_state.filter_element.get()
        self._filter_element_setting_restorer.save_by_date_filter_setting(
            current_filter_element
        )

        self.track_view_state.filter_element.set(
            FilterElement(DateRange(None, None), current_filter_element.classifications)
        )

    def enable_filter_track_by_class(self) -> None:
        """Enable filtering track by classification and restoring the previous
        classification filter setting.
        """
        current_filter_element = self.track_view_state.filter_element.get()
        restored_filter_element = (
            self._filter_element_setting_restorer.restore_by_class_filter_setting(
                current_filter_element
            )
        )
        self.track_view_state.filter_element.set(restored_filter_element)

    def disable_filter_track_by_class(self) -> None:
        """Disable filtering track by classification and saving the current
        classification filter setting."""
        current_filter_element = self.track_view_state.filter_element.get()
        self._filter_element_setting_restorer.save_by_class_filter_setting(
            current_filter_element
        )

        self.track_view_state.filter_element.set(
            FilterElement(current_filter_element.date_range, None)
        )

    def switch_to_next_date_range(self) -> None:
        """Switch to next date range in the filter setting."""
        start_date, end_date = self._get_current_date_range()
        duration = end_date - start_date

        new_date_range = DateRange(start_date + duration, end_date + duration)
        self.update_date_range_tracks_filter(new_date_range)

    def switch_to_prev_date_range(self) -> None:
        """Switch to previous date range in the filter setting."""
        start_date, end_date = self._get_current_date_range()
        duration = end_date - start_date

        new_date_range = DateRange(start_date - duration, end_date - duration)
        self.update_date_range_tracks_filter(new_date_range)

    def _get_current_date_range(self) -> tuple[datetime, datetime]:
        current_date_range = self.track_view_state.filter_element.get().date_range

        if not (start_date := current_date_range.start_date):
            if not (
                first_occurrence := self._tracks_metadata.first_detection_occurrence
            ):
                raise MissingTracksError("Unable to switch track. No tracks loaded.")

            start_date = first_occurrence

        if not (end_date := current_date_range.end_date):
            if not (last_occurrence := self._tracks_metadata.last_detection_occurrence):
                raise MissingTracksError(
                    "Unable to switch date range. No tracks loaded."
                )

            end_date = last_occurrence

        return start_date, end_date

    def get_section_offset(
        self, section_id: SectionId, event_type: EventType
    ) -> RelativeOffsetCoordinate | None:
        return self._get_section_offset.get(section_id, event_type)

    def start_new_project(self) -> None:
        self._start_new_project()

    def update_project_name(self, name: str) -> None:
        self._project_updater.update_name(name)

    def update_project_start_date(self, start_date: datetime | None) -> None:
        self._project_updater.update_start_date(start_date)

    def update_svz_metadata(self, metadata: SvzMetadata) -> None:
        self._project_updater.update_svz_metadata(metadata)

    def get_track_repository_size(self) -> int:
        return self._track_repository_size.get()

    def quick_save_configuration(self) -> None:
        self._quick_save_configuration.save()

    def config_has_changed(self) -> bool:
        return self._config_has_changed.has_changed()

    def export_road_user_assignments(self, specification: ExportSpecification) -> None:
        self._export_road_user_assignments.export(specification)

    def get_road_user_export_formats(
        self,
    ) -> Iterable[ExportFormat]:
        return self._export_road_user_assignments.get_supported_formats()

    def suggest_save_path(self, file_type: str, context_file_type: str = "") -> Path:
        """Suggests a save path based on the given file type and an optional
        related file type.

        The suggested path is in the following format:
        <BASE FOLDER>/<FILE STEM>.<CONTEXT FILE TYPE>.<FILE TYPE>

        The base folder will be determined in the following precedence:
            1. First loaded config file (otconfig or otflow)
            2. First loaded track file (ottrk)
            3. First loaded video file
            4. Default: Current working directory

        The file stem suggestion will be determined in the following precedence:
            1. The file stem of the loaded config file (otconfig or otflow)
            2. <CURRENT PROJECT NAME>_<CURRENT DATE AND TIME>
            3. Default: <CURRENT DATE AND TIME>

        Args:
            file_type (str): the file type.
            context_file_type (str): the context file type.
        """
        return self._file_name_suggester.suggest(file_type, context_file_type)

    def calculate_track_statistics(self) -> TrackStatistics:
        return self._calculate_track_statistics.get_statistics()

    def number_of_tracks_assigned_to_each_flow(self) -> dict[FlowId, int]:
        return self._number_of_tracks_assigned_to_each_flow.get()

    def export_track_statistics(
        self, specification: TrackStatisticsExportSpecification
    ) -> None:
        self._export_track_statistics.export(specification)

    def get_track_statistics_export_formats(
        self,
    ) -> Iterable[ExportFormat]:
        return self._export_track_statistics.get_supported_formats()

    def update_count_plots(self) -> None:
        self._update_count_plots.update()


class MissingTracksError(Exception):
    pass
