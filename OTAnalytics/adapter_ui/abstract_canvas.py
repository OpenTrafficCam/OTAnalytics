from abc import abstractmethod
from typing import Optional

from OTAnalytics.adapter_ui.flow_adapter import SectionRefPointCalculator
from OTAnalytics.adapter_ui.helpers import WidgetPositionProvider
from OTAnalytics.domain.section import Section

TAG_SELECTED_SECTION: str = "selected_section"


class AbstractCanvas(WidgetPositionProvider):

    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def add_preview_image(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_arrow(
        self,
        start_section: Section,
        end_section: Section,
        start_refpt_calculator: SectionRefPointCalculator,
        end_refpt_calculator: SectionRefPointCalculator,
        arrow_style: dict | None = None,
        tags: list[str] | None = None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_element(self, tag_or_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def start_section_builder(
        self,
        is_area_section: bool = False,
        section: Optional[Section] = None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def start_section_geometry_editor(
        self,
        section: Section,
        hovered_knob_style: dict | None = None,
        is_area_section: bool = False,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_section(
        self,
        id: str,
        coordinates: list[tuple[int, int]],
        is_selected_section: bool,
        is_area_section: bool = False,
        highlighted_knob_index: int | None = None,
        highlighted_knob_style: dict | None = None,
        text: str | None = None,
        tags: list[str] | None = None,
    ) -> None:
        raise NotImplementedError
