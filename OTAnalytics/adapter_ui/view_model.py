from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional

from OTAnalytics.adapter_ui.abstract_button_quick_save_config import (
    AbstractButtonQuickSaveConfig,
)
from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.abstract_frame_canvas import AbstractFrameCanvas
from OTAnalytics.adapter_ui.abstract_frame_filter import AbstractFrameFilter
from OTAnalytics.adapter_ui.abstract_frame_offset import AbstractFrameOffset
from OTAnalytics.adapter_ui.abstract_frame_project import (
    AbstractFrameProject,
    AbstractFrameSvzMetadata,
)
from OTAnalytics.adapter_ui.abstract_frame_remark import AbstractFrameRemark
from OTAnalytics.adapter_ui.abstract_frame_track_plotting import (
    AbstractFrameTrackPlotting,
)
from OTAnalytics.adapter_ui.abstract_frame_track_statistics import (
    AbstractFrameTrackStatistics,
)
from OTAnalytics.adapter_ui.abstract_main_window import AbstractMainWindow
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.text_resources import ColumnResources
from OTAnalytics.application import geometry
from OTAnalytics.application.use_cases.cut_tracks_with_sections import CutTracksDto
from OTAnalytics.application.use_cases.editor.section_editor import MetadataProvider
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.event import EventRepositoryEvent
from OTAnalytics.domain.filter import FilterElement
from OTAnalytics.domain.flow import Flow, FlowId, FlowListObserver
from OTAnalytics.domain.section import Section, SectionId, SectionListObserver
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.domain.track_repository import TrackListObserver
from OTAnalytics.domain.video import Video, VideoListObserver

DISTANCES: str = "distances"


class ViewModel(
    VideoListObserver, TrackListObserver, SectionListObserver, FlowListObserver, ABC
):

    @abstractmethod
    def show_svz(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set_window(self, window: AbstractMainWindow) -> None:
        pass

    @abstractmethod
    def set_tracks_frame(self, frame: AbstractFrame) -> None:
        pass

    @abstractmethod
    def set_offset_frame(self, offset_frame: AbstractFrameOffset) -> None:
        pass

    @abstractmethod
    def set_video_frame(self, frame: AbstractFrame) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_canvas(self, canvas: AbstractCanvas) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_treeview_sections(self, treeview: AbstractTreeviewInterface) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_sections_frame(self, frame: AbstractFrame) -> None:
        pass

    @abstractmethod
    def set_treeview_flows(self, treeview: AbstractTreeviewInterface) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_flows_frame(self, frame: AbstractFrame) -> None:
        pass

    @abstractmethod
    def set_frame_canvas(self, tracks_canvas: AbstractFrameCanvas) -> None:
        pass

    @abstractmethod
    def set_filter_frame(self, filter_frame: AbstractFrameFilter) -> None:
        pass

    @abstractmethod
    def set_frame_project(self, project_frame: AbstractFrameProject) -> None:
        pass

    @abstractmethod
    def set_frame_track_statistics(self, frame: AbstractFrameTrackStatistics) -> None:
        pass

    @abstractmethod
    def set_button_quick_save_config(
        self, button_quick_save_config: AbstractButtonQuickSaveConfig
    ) -> None:

        raise NotImplementedError

    @abstractmethod
    async def load_otconfig(self) -> None:
        pass

    @abstractmethod
    async def save_otconfig(self) -> None:
        pass

    @abstractmethod
    async def add_video(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_videos(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_treeview_videos(self, treeview: AbstractTreeviewInterface) -> None:
        pass

    @abstractmethod
    def set_selected_videos(self, video: list[str]) -> None:
        pass

    @abstractmethod
    def get_all_videos(self) -> list[Video]:
        pass

    @abstractmethod
    def get_all_track_files(self) -> set[Path]:
        pass

    @abstractmethod
    def set_treeview_files(self, treeview: AbstractTreeviewInterface) -> None:
        pass

    @abstractmethod
    def set_selected_section_ids(self, ids: list[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_selected_flow_ids(self, ids: list[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load_tracks(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load_configuration(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def save_configuration(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def quick_save_configuration(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def cancel_action(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_line_section(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_area_section(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_all_sections(self) -> Iterable[Section]:
        pass

    @abstractmethod
    async def get_section_metadata(
        self, title: str, initial_position: tuple[int, int]
    ) -> dict:
        pass

    @abstractmethod
    def update_section_coordinates(
        self, meta_data: dict, coordinates: list[tuple[int, int]]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def is_section_name_valid(self, section_name: str) -> bool:
        pass

    @abstractmethod
    async def add_new_section(
        self,
        coordinates: list[tuple[int, int]],
        is_area_section: bool,
        get_metadata: MetadataProvider,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def edit_section_geometry(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def edit_selected_section_metadata(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_sections(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def refresh_items_on_canvas(self) -> None:
        pass

    @abstractmethod
    def get_all_flows(self) -> Iterable[Flow]:
        pass

    @abstractmethod
    async def add_flow(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_remark(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate_flows(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def edit_selected_flow(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_flows(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def create_events(self) -> None:
        pass

    @abstractmethod
    def save_events(self, file: str) -> None:
        pass

    @abstractmethod
    async def export_events(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_track_offset(self, offset_x: float, offset_y: float) -> None:
        pass

    @abstractmethod
    def get_track_offset(self) -> Optional[tuple[float, float]]:
        pass

    @abstractmethod
    def change_track_offset_to_section_offset(self) -> None:
        pass

    @abstractmethod
    def validate_date(self, date: str) -> bool:
        pass

    @abstractmethod
    def validate_hour(self, hour: str) -> bool:
        pass

    @abstractmethod
    def validate_minute(self, minute: str) -> bool:
        pass

    @abstractmethod
    def validate_second(self, second: str) -> bool:
        pass

    @abstractmethod
    def apply_filter_tracks_by_date(self, date_range: DateRange) -> None:
        pass

    @abstractmethod
    def apply_filter_tracks_by_class(self, classes: list[str]) -> None:
        pass

    @abstractmethod
    def reset_filter_tracks_by_date(self) -> None:
        pass

    @abstractmethod
    def reset_filter_tracks_by_class(self) -> None:
        pass

    @abstractmethod
    def get_first_detection_occurrence(self) -> Optional[datetime]:
        pass

    @abstractmethod
    def get_last_detection_occurrence(self) -> Optional[datetime]:
        pass

    @abstractmethod
    def get_filter_tracks_by_date_setting(self) -> DateRange:
        pass

    @abstractmethod
    def get_classes(self) -> list[str]:
        pass

    @abstractmethod
    def get_class_filter_selection(self) -> Optional[list[str]]:
        pass

    @abstractmethod
    def enable_filter_track_by_date(self) -> None:
        pass

    @abstractmethod
    def disable_filter_track_by_date(self) -> None:
        pass

    @abstractmethod
    def enable_filter_track_by_class(self) -> None:
        pass

    @abstractmethod
    def disable_filter_track_by_class(self) -> None:
        pass

    @abstractmethod
    def switch_to_prev_date_range(self) -> None:
        pass

    @abstractmethod
    def switch_to_next_date_range(self) -> None:
        pass

    @abstractmethod
    async def export_counts(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def start_new_project(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_project_name(self, name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_project_start_date(self, start_date: Optional[datetime]) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_start_new_project(self, _: None) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_frame_track_plotting(
        self, frame_track_plotting: AbstractFrameTrackPlotting
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_remark_frame(self, frame: AbstractFrameRemark) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_analysis_frame(self, frame: AbstractFrame) -> None:
        raise NotImplementedError

    @abstractmethod
    def next_frame(self) -> None:
        pass

    @abstractmethod
    def previous_frame(self) -> None:
        pass

    @abstractmethod
    def next_second(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def previous_second(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def next_event(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def previous_event(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_skip_time(self, seconds: int, frames: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_skip_seconds(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def get_skip_frames(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def set_video_control_frame(self, frame: AbstractFrame) -> None:
        raise NotImplementedError

    @abstractmethod
    async def export_road_user_assignments(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_svz_metadata(self, metadata: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_directions_of_stationing(self) -> ColumnResources:
        raise NotImplementedError

    @abstractmethod
    def get_counting_day_types(self) -> ColumnResources:
        raise NotImplementedError

    @abstractmethod
    def get_weather_types(self) -> ColumnResources:
        raise NotImplementedError

    @abstractmethod
    def set_svz_metadata_frame(self, frame: AbstractFrameSvzMetadata) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_save_path_suggestion(self, file_type: str, context_file_type: str) -> Path:
        raise NotImplementedError

    @abstractmethod
    def get_tracks_assigned_to_each_flow(self) -> dict[FlowId, int]:
        raise NotImplementedError

    @abstractmethod
    async def export_track_statistics(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_flow_changed(self, flow_id: FlowId) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_background_updated(self, image: Optional[TrackImage]) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_date_range(self, filter_element: FilterElement) -> None:
        raise NotImplementedError

    @abstractmethod
    def notify_action_running_state(self, running: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_selected_videos(self, videos: list[Video]) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_selected_sections(self, section_ids: list[SectionId]) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_selected_flows(self, flow_ids: list[FlowId]) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_offset(
        self, offset: Optional[geometry.RelativeOffsetCoordinate]
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_track_statistics(self, _: EventRepositoryEvent | FilterElement) -> None:
        raise NotImplementedError

    @abstractmethod
    def change_filter_date_active(self, current: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    def on_tracks_cut(self, cut_tracks_dto: CutTracksDto) -> None:
        raise NotImplementedError

    @abstractmethod
    def register_observers(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_remark_view(self, _: Any = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_quick_save_button(self, _: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def show_current_project(self, _: Any = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_svz_metadata_view(self, _: Any = None) -> None:
        raise NotImplementedError
