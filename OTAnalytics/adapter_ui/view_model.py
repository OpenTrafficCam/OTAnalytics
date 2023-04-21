from abc import ABC, abstractmethod
from typing import Iterable, Optional

from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.adapter_ui.abstract_frame import AbstractTracksCanvas
from OTAnalytics.adapter_ui.abstract_tracks_frame import AbstractTracksFrame
from OTAnalytics.adapter_ui.abstract_treeview import AbstractTreeviewSections
from OTAnalytics.domain.section import Section


class ViewModel(ABC):
    @abstractmethod
    def register_to_subjects(self) -> None:
        pass

    @abstractmethod
    def set_tracks_frame(self, tracks_frame: AbstractTracksFrame) -> None:
        pass

    @abstractmethod
    def set_canvas(self, canvas: AbstractCanvas) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_treeview_sections(self, treeview: AbstractTreeviewSections) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_tracks_canvas(self, tracks_frame: AbstractTracksCanvas) -> None:
        pass

    @abstractmethod
    def set_selected_section_id(self, id: Optional[str]) -> None:
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
