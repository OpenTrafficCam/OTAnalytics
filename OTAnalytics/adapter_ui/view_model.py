from abc import ABC, abstractmethod
from datetime import datetime
from typing import Iterable, Optional

from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.adapter_ui.abstract_frame_canvas import AbstractFrameCanvas
from OTAnalytics.adapter_ui.abstract_frame_filter import AbstractFrameFilter
from OTAnalytics.adapter_ui.abstract_frame_tracks import AbstractFrameTracks
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.domain.date import DateRange
from OTAnalytics.domain.section import Section

DISTANCES: str = "distances"


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
    def set_treeview_flows(self, treeview: AbstractTreeviewInterface) -> None:
        raise NotImplementedError

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
    def set_new_section(self, section: Section) -> None:
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
    def refresh_sections_on_gui(self) -> None:
        pass

    @abstractmethod
    def get_all_flows(self) -> list[str]:
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
    def reset_filter_tracks_by_date(self) -> None:
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
