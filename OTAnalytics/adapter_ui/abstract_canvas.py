from abc import abstractmethod
from typing import Optional

from adapter_ui.flow_adapter import SectionRefPointCalculator
from domain.section import Section

from OTAnalytics.adapter_ui.helpers import WidgetPositionProvider

# from OTAnalytics.plugin_ui.canvas_observer import EventHandler


class AbstractCanvas(WidgetPositionProvider):
    # TODO: Properly define abstract property here and in derived class(es)
    # @property
    # @abstractmethod
    # def event_handler(self) -> EventHandler:
    #     pass

    # TODO: Define whole interface (all properties and methods) required by viewmodel

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
        style: dict,
        is_area_section: bool = False,
        section: Optional[Section] = None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def start_section_geometry_editor(
        self,
        section: Section,
        edited_section_style: dict,
        pre_edit_section_style: dict,
        selected_knob_style: dict,
        hovered_knob_style: dict | None = None,
        is_area_section: bool = False,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_section(
        self,
        id: str,
        coordinates: list[tuple[int, int]],
        section_style: dict,
        is_area_section: bool = False,
        highlighted_knob_index: int | None = None,
        highlighted_knob_style: dict | None = None,
        text: str | None = None,
        tags: list[str] | None = None,
    ) -> None:
        raise NotImplementedError
