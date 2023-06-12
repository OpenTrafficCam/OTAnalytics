from abc import ABC, abstractmethod
from datetime import datetime
from typing import Callable, Iterable, Optional

from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.adapter_ui.abstract_frame_canvas import AbstractFrameCanvas
from OTAnalytics.adapter_ui.abstract_frame_filter import AbstractFrameFilter
from OTAnalytics.adapter_ui.abstract_frame_flows import AbstractFrameFlows
from OTAnalytics.adapter_ui.abstract_frame_sections import AbstractFrameSections
from OTAnalytics.adapter_ui.abstract_frame_tracks import AbstractFrameTracks
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.flow import Flow
from OTAnalytics.domain.section import Section

DISTANCES: str = "distances"


MetadataProvider = Callable[[], dict]


class MissingCoordinate(Exception):
    pass


class ViewModel(ABC):
    @abstractmethod
    def register_to_subjects(self) -> None:
        pass

    @abstractmethod
    def set_tracks_frame(self, tracks_frame: AbstractFrameTracks) -> None:
        pass

    @abstractmethod
    def set_canvas(self, canvas: AbstractCanvas) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_treeview_sections(self, treeview: AbstractTreeviewInterface) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_sections_frame(self, frame: AbstractFrameSections) -> None:
        pass

    @abstractmethod
    def set_treeview_flows(self, treeview: AbstractTreeviewInterface) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_flows_frame(self, frame: AbstractFrameFlows) -> None:
        pass

    @abstractmethod
    def set_tracks_canvas(self, tracks_canvas: AbstractFrameCanvas) -> None:
        pass

    @abstractmethod
    def set_filter_frame(self, filter_frame: AbstractFrameFilter) -> None:
        pass

    @abstractmethod
    def set_selected_section_id(self, id: Optional[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_selected_flow_id(self, id: Optional[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_tracks(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_sections(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_sections(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_section(self) -> None:
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
        self, coordinates: list[tuple[int, int]], get_metadata: MetadataProvider
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def edit_section_geometry(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def edit_section_metadata(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_section(self) -> None:
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
    def edit_flow(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def remove_flow(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def start_analysis(self) -> None:
        pass

    @abstractmethod
    def save_events(self, file: str) -> None:
        pass

    @abstractmethod
    def update_show_tracks_state(self, value: bool) -> None:
        pass

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
