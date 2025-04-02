from typing import Self, Iterable

from nicegui import ui
from nicegui.elements.button import Button

from OTAnalytics.adapter_ui.abstract_frame_section import AbstractSectionFrame
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.text_resources import COLUMN_NAME
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import ResourceManager, SectionKeys
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import Section
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import CustomTable
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import CanvasForm


COLUMN_NAME = "name"


class SectionsForm(AbstractFrameSvzMetadata):
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
            rows=map_to_ui(self._view_model.get_all_sections()),
            on_select_method=lambda e: self._select_section(e),
            selection="single"
        )
        self._canvas_form = canvas_form
        self._button_edit: ui.button | None = None
        self._button_properties: ui.button | None = None
        self._current_section: Section
        self._result: dict = {}
        self._introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._view_model.set_svz_metadata_frame(self)

    def build(self) -> Self:
        self._section_table.build()
        with ui.grid(rows=3):
            with ui.row():
                ui.button(self._resource_manager.get(SectionKeys.BUTTON_ADD_LINE), on_click=self.add_new_line)# Enter für bestätigen und escape
                ui.button(self._resource_manager.get(SectionKeys.BUTTON_ADD_AREA), on_click=self.add_new_area)
            with ui.row():
                self._button_edit = ui.button(self._resource_manager.get(SectionKeys.BUTTON_EDIT), on_click=self.edit_section)# Toggle Button
                self._button_properties = ui.button(self._resource_manager.get(SectionKeys.BUTTON_PROPERTIES), on_click=self.edit_properties)
            with ui.row():
                ui.button(self._resource_manager.get(SectionKeys.BUTTON_REMOVE), on_click=self.remove_section)
        return self

    def update(self, metadata: dict) -> None:

        self._section_table.update(map_to_ui(self._view_model.get_all_sections()))

    def add_new_line(self) -> None:
        self._section_table.update(map_to_ui(self._view_model.get_all_sections()))
        self._view_model.refresh_items_on_canvas()
        self._canvas_form.add_new_section()
    def add_new_area(self) -> None:
        self._canvas_form.add_new_section(is_area_section=True)
    def edit_section(self) -> None:
        self.open_dialog()
    def edit_properties(self) -> None:
        self.open_dialog()

    def open_dialog(self) -> None:
        def apply_changes() -> None:
            self._result = self._current_section
            self._result["name"] = self._properties_name.value
            self._result["relative_offset_coordinates"] = {"section-enter": {
                        "x": self._x_offset_slider.value,
                        "y": self._y_offset_slider.value
                    }}
            self._dialog.close()
            self._view_model.edit_selected_section_metadata()
        self._dialog = ui.dialog()
        with self._dialog, ui.card():
            self._properties_name = ui.input(value=self._current_section["name"])
            ui.label("X Value")
            self._x_offset_slider = ui.slider(
                min=0, max=1, step=0.1,
                value=self._current_section["relative_offset_coordinates"]["section-enter"]["x"],
            )
            ui.label("Y Value")
            self._y_offset_slider = ui.slider(
                min=0, max=1, step=0.1,
                value=self._current_section["relative_offset_coordinates"]["section-enter"]["y"],
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
        pass
    def remove_section(self) -> None:
        self._view_model.remove_sections()
        self._view_model.refresh_items_on_canvas()
    def get_add_buttons(self) -> list[Button]:
        return []

    def get_single_item_buttons(self) -> list[Button]:
        if self._button_edit and self._button_properties:
            return [self._button_edit, self._button_properties]
        else:
            return []

    def get_multiple_items_buttons(self) -> list[Button]:
        return []

