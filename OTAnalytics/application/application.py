from abc import ABC
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

from OTAnalytics.application.analysis.intersect import (
    RunIntersect,
    RunSceneEventDetection,
)
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
    ExportCounts,
    ExportFormat,
)
from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.generate_flows import GenerateFlows
from OTAnalytics.application.state import (
    ActionState,
    FlowState,
    SectionState,
    TracksMetadata,
    TrackState,
    TrackViewState,
)
from OTAnalytics.application.use_cases.config import SaveOtconfig
from OTAnalytics.application.use_cases.export_events import EventListExporter
from OTAnalytics.application.use_cases.update_project import ProjectUpdater
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.event import EventRepository
from OTAnalytics.domain.filter import FilterElement, FilterElementSettingRestorer
from OTAnalytics.domain.flow import (
    Flow,
    FlowChangedObserver,
    FlowId,
    FlowListObserver,
    FlowRepository,
)
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import (
    Section,
    SectionChangedObserver,
    SectionId,
    SectionListObserver,
    SectionRepository,
)
from OTAnalytics.domain.track import TrackId, TrackImage, TrackListObserver
from OTAnalytics.domain.types import EventType
from OTAnalytics.domain.video import Video, VideoListObserver


class SectionAlreadyExists(Exception):
    pass


class CancelAddSection(Exception):
    pass


class CancelAddFlow(Exception):
    pass


class FlowAlreadyExists(Exception):
    pass


class MultipleSectionsSelected(Exception):
    pass


class MultipleFlowsSelected(Exception):
    pass


class AddSection:
    """
    Add a single section to the repository.
    """

    def __init__(self, section_repository: SectionRepository) -> None:
        self._section_repository = section_repository

    def add(self, section: Section) -> None:
        if not self.is_section_name_valid(section.name):
            raise SectionAlreadyExists(
                f"A section with the name {section.name} already exists. "
                "Choose another name."
            )
        self._section_repository.add(section)

    def is_section_name_valid(self, section_name: str) -> bool:
        if not section_name:
            return False
        return all(
            stored_section.name != section_name
            for stored_section in self._section_repository.get_all()
        )


class AddFlow:
    """
    Add a single flow to the repository.
    """

    def __init__(self, flow_repository: FlowRepository) -> None:
        self._flow_repository = flow_repository

    def add(self, flow: Flow) -> None:
        if not self.is_flow_name_valid(flow.name):
            raise FlowAlreadyExists(
                f"A flow with the name {flow.name} already exists. "
                "Choose another name."
            )
        self._flow_repository.add(flow)

    def is_flow_name_valid(self, flow_name: str) -> bool:
        if not flow_name:
            return False
        return all(
            stored_flow.name != flow_name
            for stored_flow in self._flow_repository.get_all()
        )


class ClearEventRepository(SectionListObserver, TrackListObserver):
    """Clears the event repository also on section state changes.

    Args:
        event_repository (EventRepository): the event repository
    """

    def __init__(self, event_repository: EventRepository) -> None:
        self._event_repository = event_repository

    def clear(self) -> None:
        self._event_repository.clear()

    def notify_sections(self, sections: list[SectionId]) -> None:
        self.clear()

    def notify_tracks(self, tracks: list[TrackId]) -> None:
        self.clear()

    def on_section_changed(self, section_id: SectionId) -> None:
        self.clear()


class IntersectTracksWithSections(ABC):
    def run(self) -> None:
        raise NotImplementedError


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
        intersect: RunIntersect,
        scene_event_detection: RunSceneEventDetection,
        tracks_metadata: TracksMetadata,
        action_state: ActionState,
        filter_element_setting_restorer: FilterElementSettingRestorer,
        generate_flows: GenerateFlows,
        intersect_tracks_with_sections: IntersectTracksWithSections,
        export_counts: ExportCounts,
    ) -> None:
        self._datastore: Datastore = datastore
        self.track_state: TrackState = track_state
        self.track_view_state: TrackViewState = track_view_state
        self.section_state: SectionState = section_state
        self.flow_state: FlowState = flow_state
        self._intersect = intersect
        self._scene_event_detection = scene_event_detection
        self._tracks_metadata = tracks_metadata
        self.action_state = action_state
        self._filter_element_setting_restorer = filter_element_setting_restorer
        self._add_section = AddSection(self._datastore._section_repository)
        self._add_flow = AddFlow(self._datastore._flow_repository)
        self._generate_flows = generate_flows
        self._intersect_tracks_with_sections = intersect_tracks_with_sections
        self._clear_event_repository = ClearEventRepository(
            self._datastore._event_repository
        )
        self._export_counts = export_counts
        self._project_updater = ProjectUpdater(datastore)
        self._save_otconfig = SaveOtconfig(
            datastore, config_parser=datastore._config_parser
        )

    def connect_observers(self) -> None:
        """
        Connect the observers with the repositories to listen to domain object changes.
        """
        self._datastore.register_tracks_observer(self.track_state)
        self._datastore.register_tracks_observer(self._tracks_metadata)
        self._datastore.register_sections_observer(self.section_state)

    def connect_clear_event_repository_observer(self) -> None:
        self._datastore.register_sections_observer(self._clear_event_repository)
        self._datastore.register_section_changed_observer(
            self._clear_event_repository.on_section_changed
        )
        self._datastore.register_tracks_observer(self._clear_event_repository)

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

    def get_all_sections(self) -> Iterable[Section]:
        return self._datastore.get_all_sections()

    def get_section_for(self, section_id: SectionId) -> Optional[Section]:
        return self._datastore.get_section_for(section_id)

    def add_videos(self, files: list[Path]) -> None:
        self._datastore.load_video_files(files)

    def remove_videos(self) -> None:
        """
        Remove the currently selected videos from the repository.
        """
        if videos := self.track_view_state.selected_videos.get():
            self._datastore.remove_videos(videos)
            if videos := self._datastore.get_all_videos():
                self.track_view_state.selected_videos.set([videos[0]])
            else:
                self.track_view_state.selected_videos.set([])

    def get_all_videos(self) -> list[Video]:
        return self._datastore.get_all_videos()

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
        self._add_flow.add(flow)

    def generate_flows(self) -> None:
        self._generate_flows.generate()

    def remove_flow(self, flow_id: FlowId) -> None:
        self._datastore.remove_flow(flow_id)

    def update_flow(self, flow: Flow) -> None:
        self._datastore.update_flow(flow)

    def update_project(self, name: str, start_date: Optional[datetime]) -> None:
        self._project_updater(name, start_date)

    def save_otconfig(self, file: Path) -> None:
        self._save_otconfig(file)

    def load_otconfig(self, file: Path) -> None:
        self._datastore.load_otconfig(file)

    def add_tracks_of_file(self, track_file: Path) -> None:
        """
        Load a single track file.

        Args:
            track_file (Path): file in ottrk format
        """
        self._datastore.load_track_file(file=track_file)

    def add_tracks_of_files(self, track_files: list[Path]) -> None:
        """
        Load a multiple track files.

        Args:
            track_files (list[Path]): files in ottrk format
        """
        self._datastore.load_track_files(files=track_files)

    def delete_all_tracks(self) -> None:
        """Delete all tracks."""
        self._datastore.delete_all_tracks()

    def load_otflow(self, sections_file: Path) -> None:
        """
        Load sections from a sections file.

        Args:
            sections_file (Path): file in sections format
        """
        self._datastore.load_otflow(file=sections_file)

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
        self._add_section.add(section)

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
        self._datastore.save_flow_file(file)

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
        tracks = self._datastore.get_all_tracks().as_list()
        sections = self._datastore.get_all_sections()
        events = self._intersect.run(tracks, sections)
        self._clear_event_repository.clear()
        self._datastore.add_events(events)

        scene_events = self._scene_event_detection.run(
            self._datastore.get_all_tracks().as_list()
        )
        self._datastore.add_events(scene_events)

    def intersect_tracks_with_sections(self) -> None:
        self._intersect_tracks_with_sections.run()

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
        current_filter_element = self.track_view_state.filter_element.get()
        restored_filter_element = (
            self._filter_element_setting_restorer.restore_by_date_filter_setting(
                current_filter_element
            )
        )
        self.track_view_state.filter_element.set(restored_filter_element)

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


class MissingTracksError(Exception):
    pass
