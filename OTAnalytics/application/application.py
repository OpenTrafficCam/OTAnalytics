from pathlib import Path
from typing import Iterable, Optional

from OTAnalytics.application.analysis.intersect import (
    RunIntersect,
    RunSceneEventDetection,
)
from OTAnalytics.application.datastore import Datastore
from OTAnalytics.application.state import (
    SectionState,
    TracksMetadata,
    TrackState,
    TrackViewState,
)
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.filter import FilterElement, FilterElementSettingRestorer
from OTAnalytics.domain.flow import Flow, FlowId, FlowListObserver
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import (
    Section,
    SectionChangedObserver,
    SectionId,
    SectionListObserver,
)
from OTAnalytics.domain.track import TrackId, TrackImage
from OTAnalytics.domain.types import EventType


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
        intersect: RunIntersect,
        scene_event_detection: RunSceneEventDetection,
        tracks_metadata: TracksMetadata,
        filter_element_setting_restorer: FilterElementSettingRestorer,
    ) -> None:
        self._datastore: Datastore = datastore
        self.track_state: TrackState = track_state
        self.track_view_state: TrackViewState = track_view_state
        self.section_state: SectionState = section_state
        self._intersect = intersect
        self._scene_event_detection = scene_event_detection
        self._tracks_metadata = tracks_metadata
        self._filter_element_setting_restorer = filter_element_setting_restorer

    def connect_observers(self) -> None:
        """
        Connect the observers with the repositories to listen to domain object changes.
        """
        self._datastore.register_tracks_observer(self.track_state)
        self._datastore.register_tracks_observer(self._tracks_metadata)
        self._datastore.register_sections_observer(self.section_state)

    def register_sections_observer(self, observer: SectionListObserver) -> None:
        self._datastore.register_sections_observer(observer)

    def register_section_changed_observer(
        self, observer: SectionChangedObserver
    ) -> None:
        self._datastore.register_section_changed_observer(observer)

    def register_flows_observer(self, observer: FlowListObserver) -> None:
        self._datastore.register_flows_observer(observer)

    def get_all_sections(self) -> Iterable[Section]:
        return self._datastore.get_all_sections()

    def get_section_for(self, section_id: SectionId) -> Optional[Section]:
        return self._datastore.get_section_for(section_id)

    def get_all_flows(self) -> Iterable[Flow]:
        return self._datastore.get_all_flows()

    def get_flow_for(self, flow_id: FlowId) -> Optional[Flow]:
        return self._datastore.get_flow_for(flow_id)

    def add_flow(self, flow: Flow) -> None:
        self._datastore.add_flow(flow)

    def remove_flow(self, flow_id: FlowId) -> None:
        self._datastore.remove_flow(flow_id)

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

    def add_sections_of_file(self, sections_file: Path) -> None:
        """
        Load sections from a sections file.

        Args:
            sections_file (Path): file in sections format
        """
        self._datastore.load_section_file(file=sections_file)

    def add_section(self, section: Section) -> None:
        """
        Add a new section

        Args:
            section (Section): section to add
        """
        self._datastore.add_section(section)

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

    def save_flows(self, file: Path) -> None:
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
        tracks = self._datastore.get_all_tracks()
        sections = self._datastore.get_all_sections()
        events = self._intersect.run(tracks, sections)
        self._datastore.add_events(events)

        scene_events = self._scene_event_detection.run(self._datastore.get_all_tracks())
        self._datastore.add_events(scene_events)

    def save_events(self, file: Path) -> None:
        """
        Save the event repository into a file.

        Args:
            file (Path): file to save the events to
        """
        self._datastore.save_event_list_file(file)

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
        if section_id := self.section_state.selected_section.get():
            if section := self._datastore.get_section_for(section_id):
                if offset := section.relative_offset_coordinates.get(event_type):
                    self.track_view_state.track_offset.set(offset)

    def set_selected_section(self, id: Optional[str]) -> None:
        """Set the current selected section in the UI.

        Args:
            id (SectionId): the id of the currently selected section
        """
        if id:
            section_id = SectionId(id)
        else:
            section_id = None

        self.section_state.selected_section.set(section_id)

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
