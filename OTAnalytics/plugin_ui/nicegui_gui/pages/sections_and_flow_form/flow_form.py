from typing import Iterable, Self

from nicegui import ui
from nicegui.elements.button import Button

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import FlowKeys, ResourceManager
from OTAnalytics.domain.flow import Flow
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import CustomTable

COLUMN_ID = "id"
COLUMN_NAME = "name"


def create_columns(resource_manager: ResourceManager) -> list[dict[str, str]]:
    return [
        {
            "name": COLUMN_NAME,
            "label": resource_manager.get(FlowKeys.TABLE_COLUMN_NAME),
            "field": "name",
        },
    ]


def map_to_ui(flows: Iterable[Flow]) -> list:
    list_of_flows = []
    for flow in flows:
        list_of_flows.append(flow.to_dict())
    return list_of_flows


class FlowForm(ButtonForm, AbstractFrame, AbstractTreeviewInterface):
    def __init__(
        self,
        view_model: ViewModel,
        resource_manager: ResourceManager,
    ) -> None:
        self._view_model = view_model
        self._resource_manager = resource_manager
        self._flow_table = CustomTable(
            columns=create_columns(resource_manager),
            rows=[],
            on_select_method=lambda e: self._select_flow(e.selection),
            selection="single",
        )
        self._button_remove: ui.button | None = None
        self._button_add: ui.button | None = None
        self._button_generate: ui.button | None = None
        self._button_properties: ui.button | None = None
        self._introduce_to_viewmodel()

    def _introduce_to_viewmodel(self) -> None:
        self._view_model.set_flows_frame(self)
        self._view_model.set_treeview_flows(self)

    def _select_flow(self, e: dict) -> None:
        flow_ids = [event[COLUMN_ID] for event in e]
        self._view_model.set_selected_flow_ids(flow_ids)
        self._view_model.refresh_items_on_canvas()

    def build(self) -> Self:
        self._flow_table.build()
        with ui.row():
            self._button_add = ui.button(
                self._resource_manager.get(FlowKeys.BUTTON_ADD), on_click=self.add_flow
            )
            self._button_generate = ui.button(
                self._resource_manager.get(FlowKeys.BUTTON_GENERATE),
                on_click=self.generate_flow,
            )
        self._button_remove = ui.button(
            self._resource_manager.get(FlowKeys.BUTTON_REMOVE),
            on_click=self.remove_flow,
        )
        self._button_properties = ui.button(
            self._resource_manager.get(FlowKeys.BUTTON_PROPERTIES),
            on_click=self.show_flow_properties,
        )
        self.update({})
        return self

    def update(self, metadata: dict) -> None:
        self._flow_table.update(map_to_ui(self._view_model.get_all_flows()))

    def add_flow(self) -> None:

        self._flow_table.update(map_to_ui(self._view_model.get_all_flows()))

    def generate_flow(self) -> None:
        self._view_model.generate_flows()

    def remove_flow(self) -> None:
        self._view_model.remove_flows()

    def show_flow_properties(self) -> None:
        self._view_model.edit_selected_flow()

    def set_enabled_general_buttons(self, enabled: bool) -> None:
        pass

    def set_enabled_change_multiple_items_buttons(self, enabled: bool) -> None:
        pass

    def set_enabled_change_single_item_buttons(self, enabled: bool) -> None:
        pass

    def set_enabled_add_buttons(self, enabled: bool) -> None:
        pass

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        pass

    def update_items(self) -> None:
        pass
        # self._flow_table.update(map_to_ui(self._view_model.get_all_flows()))

    def update_selected_items(self, item_ids: list[str]) -> None:
        pass

    def enable(self) -> None:
        if (
            self._button_remove
            and self._button_properties
            and self._button_add
            and self._button_generate
        ):
            self._button_remove.enable()
            self._button_add.enable()
            self._button_generate.enable()
            self._button_properties.enable()

    def disable(self) -> None:
        if (
            self._button_remove
            and self._button_properties
            and self._button_add
            and self._button_generate
        ):
            self._button_remove.disable()
            self._button_add.disable()
            self._button_generate.disable()
            self._button_properties.disable()

    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        return 0, 0

    def get_add_buttons(self) -> list[Button]:
        if self._button_add:
            return [self._button_add]
        return []

    def get_single_item_buttons(self) -> list[Button]:
        if self._button_remove and self._button_properties:
            return [self._button_remove, self._button_properties]
        return []

    def get_multiple_items_buttons(self) -> list[Button]:
        return []
