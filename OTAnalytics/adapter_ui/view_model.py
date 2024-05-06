from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Callable, Iterable, Optional

from OTAnalytics.adapter_ui.abstract_button_quick_save_config import (
    AbstractButtonQuickSaveConfig,
)
from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.abstract_frame_canvas import AbstractFrameCanvas
from OTAnalytics.adapter_ui.abstract_frame_filter import AbstractFrameFilter
from OTAnalytics.adapter_ui.abstract_frame_project import (
    AbstractFrameProject,
    AbstractFrameSvzMetadata,
)
from OTAnalytics.adapter_ui.abstract_frame_track_plotting import (
    AbstractFrameTrackPlotting,
)
from OTAnalytics.adapter_ui.abstract_frame_tracks import AbstractFrameTracks
from OTAnalytics.adapter_ui.abstract_main_window import AbstractMainWindow
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.text_resources import ColumnResources
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.video import Video

DISTANCES: str = "distances"

MetadataProvider = Callable[[], dict]


class MissingCoordinate(Exception):
    pass


class ViewModel(ABC):
    @abstractmethod
    def set_window(self, window: AbstractMainWindow) -> None:
        pass

    @abstractmethod
    def set_tracks_frame(self, tracks_frame: AbstractFrameTracks) -> None:
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
    def set_button_quick_save_config(
        self, button_quick_save_config: AbstractButtonQuickSaveConfig
    ) -> None:

        raise NotImplementedError

    @abstractmethod
    def load_otconfig(self) -> None:
        pass

    @abstractmethod
    def save_otconfig(self) -> None:
        pass

    @abstractmethod
    def add_video(self) -> None:
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
    def load_tracks(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_configuration(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_configuration(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def quick_save_configuration(self) -> None:
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
    def get_section_metadata(
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
    def add_new_section(
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
    def edit_selected_section_metadata(self) -> None:
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
    def add_flow(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def generate_flows(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def edit_selected_flow(self) -> None:
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
    def export_events(self) -> None:
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
    def export_counts(self) -> None:
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
    def export_road_user_assignments(self) -> None:
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
