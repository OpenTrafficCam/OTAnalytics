from typing import Iterable, Self

from nicegui import ui
from nicegui.elements.button import Button

from OTAnalytics.adapter_ui.abstract_frame_section import AbstractSectionFrame
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    SectionKeys,
)
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import CustomTable
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (
    CanvasForm,
)

COLUMN_SECTION_NAME = "name"


def create_columns(resource_manager: ResourceManager) -> list[dict[str, str]]:

    return [
        {
            "name": COLUMN_SECTION_NAME,
            "label": resource_manager.get(SectionKeys.TABLE_COLUMN_NAME),
            "field": "name",
        },
    ]


def map_to_ui(sections: Iterable[Section]) -> list:
    list_of_sections = []
    for section in sections:
        list_of_sections.append(section.to_dict())
    return list_of_sections


class SectionsForm(ButtonForm, AbstractTreeviewInterface, AbstractSectionFrame):
    def __init__(
        self,
        view_model: ViewModel,
        resource_manager: ResourceManager,
        canvas_form: CanvasForm,
    ) -> None:
        self._view_model = view_model
        self._resource_manager = resource_manager
        self._section_table = CustomTable(
            columns=create_columns(resource_manager),
            rows=[],
            on_select_method=lambda e: self._select_section(e.selection),
            selection="single",
        )
        self._canvas_form = canvas_form
        self._toggle = False
        self._button_edit: ui.button | None = None
        self._button_properties: ui.button | None = None
        self._button_add_areas: ui.button | None = None
        self._button_add_line: ui.button | None = None
        self._button_remove: ui.button | None = None
        self._current_section: Section
        self._result: dict = {}
        self._introduce_to_viewmodel()

    def _introduce_to_viewmodel(self) -> None:
        self._view_model.set_sections_frame(self)
        self._view_model.set_treeview_sections(self)

    def _select_section(self, e: dict) -> None:
        self._current_section = e[0]
        self._view_model.set_selected_section_ids(e[0]["id"])
        self._view_model.refresh_items_on_canvas()

    def build(self) -> Self:
        self._section_table.build()
        with ui.grid(rows=3):
            with ui.row():
                self._button_add_line = ui.button(
                    self._resource_manager.get(SectionKeys.BUTTON_ADD_LINE),
                    on_click=self.add_new_line,
                )
                self._button_add_areas = ui.button(
                    self._resource_manager.get(SectionKeys.BUTTON_ADD_AREA),
                    on_click=self.add_new_area,
                )
            with ui.row():
                self._button_edit = ui.button(
                    self._resource_manager.get(SectionKeys.BUTTON_EDIT),
                    on_click=self.edit_section,
                )  # Toggle Button
                self._button_properties = ui.button(
                    self._resource_manager.get(SectionKeys.BUTTON_PROPERTIES),
                    on_click=self.edit_properties,
                )
            with ui.row():
                self._button_remove = ui.button(
                    self._resource_manager.get(SectionKeys.BUTTON_REMOVE),
                    on_click=self.remove_section,
                )
        self.update({})
        return self

    def update(self, metadata: dict) -> None:

        self._section_table.update(map_to_ui(self._view_model.get_all_sections()))

    def add_new_line(self) -> None:
        if self._toggle:
            pass
        else:
            self._section_table.update(map_to_ui(self._view_model.get_all_sections()))
            self._view_model.refresh_items_on_canvas()
            # self._canvas_form.add_new_section(area_section=False)
            self._toggle = True

    def add_new_area(self) -> None:
        # self._canvas_form.add_new_section(area_section=True)
        pass

    def edit_section(self) -> None:
        self.open_dialog()

    def edit_properties(self) -> None:
        self.open_dialog()

    def open_dialog(self) -> None:
        def apply_changes() -> None:
            self._result = self._current_section.to_dict()
            self._result["name"] = self._properties_name.value
            self._result["relative_offset_coordinates"] = {
                "section-enter": {
                    "x": self._x_offset_slider.value,
                    "y": self._y_offset_slider.value,
                }
            }
            self._dialog.close()
            self._view_model.edit_selected_section_metadata()

        self._dialog = ui.dialog()
        with self._dialog, ui.card():
            current_section = self._current_section.to_dict()
            self._properties_name = ui.input(value=current_section["name"])
            ui.label("X Value")
            self._x_offset_slider = ui.slider(
                min=0,
                max=1,
                step=0.1,
                value=current_section["relative_offset_coordinates"]["section-enter"][
                    "x"
                ],
            )
            ui.label("Y Value")
            self._y_offset_slider = ui.slider(
                min=0,
                max=1,
                step=0.1,
                value=current_section["relative_offset_coordinates"]["section-enter"][
                    "y"
                ],
            )
            ui.button("Apply Changes", on_click=apply_changes)
        self._dialog.open()

    def configure_section(
        self,
        title: str,
        section_offset: RelativeOffsetCoordinate,
        initial_position: tuple[int, int],
        input_values: dict | None,
        show_offset: bool,
    ) -> dict:
        return self._result

    def _save_sections(self) -> dict:
        return {}

    def remove_section(self) -> None:
        self._view_model.remove_sections()
        self._view_model.refresh_items_on_canvas()

    def get_add_buttons(self) -> list[Button]:
        if self._button_add_line and self._button_add_areas:
            return [self._button_add_line, self._button_add_areas]
        return []

    def get_single_item_buttons(self) -> list[Button]:
        if self._button_edit and self._button_properties:
            return [self._button_edit, self._button_properties]
        return []

    def get_multiple_items_buttons(self) -> list[Button]:
        return []

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        pass

    def update_selected_items(self, item_ids: list[str]) -> None:
        pass

    def update_items(self) -> None:
        pass

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
