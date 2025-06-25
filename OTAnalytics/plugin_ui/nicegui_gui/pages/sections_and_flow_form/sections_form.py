from typing import Any, Iterable, Self

from nicegui import ui
from nicegui.elements.button import Button

from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    SectionKeys,
)
from OTAnalytics.application.state import SectionState
from OTAnalytics.domain.section import NAME, Section
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import (
    COLUMN_ID,
    CustomTable,
)

BUTTON_WIDTH = "max-width: 45%; width: 100%"
BASIC_WIDTH = "width: 100%"
MARKER_SECTION_TABLE = "marker-section-table"
MARKER_BUTTON_ADD_LINE = "marker-button-add-line"
MARKER_BUTTON_ADD_AREA = "marker-button-add-area"
MARKER_BUTTON_EDIT = "marker-button-edit"
MARKER_BUTTON_PROPERTIES = "marker-button-properties"
MARKER_BUTTON_REMOVE = "marker-button-remove"


def create_columns(resource_manager: ResourceManager) -> list[dict[str, str]]:

    return [
        {
            "name": NAME,
            "label": resource_manager.get(SectionKeys.TABLE_COLUMN_NAME),
            "field": "name",
        },
    ]


def map_to_ui(sections: Iterable[Section]) -> list:
    list_of_sections = []
    for section in sections:
        list_of_sections.append(section.to_dict())
    return list_of_sections


class SectionsForm(ButtonForm, AbstractTreeviewInterface):
    def __init__(
        self,
        viewmodel: ViewModel,
        section_state: SectionState,
        resource_manager: ResourceManager,
    ) -> None:
        self._viewmodel = viewmodel
        self._section_state = section_state
        self._resource_manager = resource_manager
        self._section_table = CustomTable(
            columns=create_columns(resource_manager),
            rows=[],
            on_select_method=lambda e: self._select_section(e.selection),
            selection="single",
            marker=MARKER_SECTION_TABLE,
        )
        self._toggle = False
        self._button_edit: ui.button | None = None
        self._button_properties: ui.button | None = None
        self._button_add_areas: ui.button | None = None
        self._button_add_line: ui.button | None = None
        self._button_remove: ui.button | None = None
        self._result: dict = {}
        self._introduce_to_viewmodel()

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_sections_frame(self)
        self._viewmodel.set_treeview_sections(self)

    def _select_section(self, events: list[dict[str, Any]]) -> None:
        selected_sections = [event[COLUMN_ID] for event in events]
        self._viewmodel.set_selected_section_ids(selected_sections)

    def build(self) -> Self:
        self._section_table.build()
        with ui.grid(rows=3).style(BASIC_WIDTH):
            with ui.row().style(BASIC_WIDTH):
                self._button_add_line = ui.button(
                    self._resource_manager.get(SectionKeys.BUTTON_ADD_LINE),
                    on_click=self._viewmodel.add_line_section,
                ).style(BUTTON_WIDTH)
                self._button_add_line.mark(MARKER_BUTTON_ADD_LINE)

                self._button_add_areas = ui.button(
                    self._resource_manager.get(SectionKeys.BUTTON_ADD_AREA),
                    on_click=self._viewmodel.add_area_section,
                ).style(BUTTON_WIDTH)
                self._button_add_areas.mark(MARKER_BUTTON_ADD_AREA)

            with ui.row().style(BASIC_WIDTH):
                self._button_edit = ui.button(
                    self._resource_manager.get(SectionKeys.BUTTON_EDIT),
                    on_click=self._viewmodel.edit_section_geometry,
                ).style(BUTTON_WIDTH)
                self._button_edit.mark(MARKER_BUTTON_EDIT)

                self._button_properties = ui.button(
                    self._resource_manager.get(SectionKeys.BUTTON_PROPERTIES),
                    on_click=self._viewmodel.edit_selected_section_metadata,
                ).style(BUTTON_WIDTH)
                self._button_properties.mark(MARKER_BUTTON_PROPERTIES)

            with ui.row().style(BASIC_WIDTH):
                self._button_remove = ui.button(
                    self._resource_manager.get(SectionKeys.BUTTON_REMOVE),
                    on_click=self._viewmodel.remove_sections,
                ).style(BASIC_WIDTH)
                self._button_remove.mark(MARKER_BUTTON_REMOVE)
        self.update_items()
        return self

    def get_add_buttons(self) -> list[Button]:
        if self._button_add_line and self._button_add_areas:
            return [self._button_add_line, self._button_add_areas]
        return []

    def get_single_item_buttons(self) -> list[Button]:
        if self._button_edit and self._button_properties:
            return [self._button_edit, self._button_properties]
        return []

    def get_multiple_items_buttons(self) -> list[Button]:
        if self._button_remove:
            return [self._button_remove]
        return []

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        self._viewmodel.set_selected_section_ids(ids)

    def update_selected_items(self, item_ids: list[str]) -> None:
        self._section_table.select(item_ids)

    def update_items(self) -> None:
        self._section_table.update(map_to_ui(self._viewmodel.get_all_sections()))
        selected_sections = [
            section.id for section in self._section_state.selected_sections.get()
        ]
        self.update_selected_items(selected_sections)

    def disable(self) -> None:
        if (
            self._button_add_line
            and self._button_add_line
            and self._button_add_areas
            and self._button_remove
        ):
            self._button_add_line.disable()
            self._button_add_line.disable()
            self._button_add_areas.disable()
            self._button_remove.disable()

    def enable(self) -> None:
        if (
            self._button_add_line
            and self._button_add_line
            and self._button_add_areas
            and self._button_remove
        ):
            self._button_add_line.enable()
            self._button_add_line.enable()
            self._button_add_areas.enable()
            self._button_remove.enable()

    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        return 0, 0
