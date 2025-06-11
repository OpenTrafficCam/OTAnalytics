from typing import Iterable, Self

from nicegui import ui
from nicegui.elements.button import Button
from nicegui.events import ClickEventArguments

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import FlowKeys, ResourceManager
from OTAnalytics.application.state import FlowState
from OTAnalytics.domain.flow import FLOW_NAME, Flow
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import (
    COLUMN_ID,
    CustomTable,
)

BUTTON_WIDTH = "max-width: 45%; width: 100%"
BASIC_WIDTH = "width: 100%"
MARKER_FLOW_TABLE = "marker-flow-table"
MARKER_BUTTON_ADD = "marker-button-add"
MARKER_BUTTON_GENERATE = "marker-button-generate"
MARKER_BUTTON_REMOVE = "marker-button-remove"
MARKER_BUTTON_PROPERTIES = "marker-button-properties"


def create_columns(resource_manager: ResourceManager) -> list[dict[str, str]]:
    return [
        {
            "name": FLOW_NAME,
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
        viewmodel: ViewModel,
        flow_state: FlowState,
        resource_manager: ResourceManager,
    ) -> None:
        self._viewmodel = viewmodel
        self._flow_state = flow_state
        self._resource_manager = resource_manager
        self._flow_table = CustomTable(
            columns=create_columns(resource_manager),
            rows=[],
            on_select_method=lambda e: self._select_flow(e.selection),
            selection="single",
            marker=MARKER_FLOW_TABLE,
        )
        self._button_remove: ui.button | None = None
        self._button_add: ui.button | None = None
        self._button_generate: ui.button | None = None
        self._button_properties: ui.button | None = None
        self._introduce_to_viewmodel()

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_flows_frame(self)
        self._viewmodel.set_treeview_flows(self)

    def _select_flow(self, e: dict) -> None:
        flow_ids = [event[COLUMN_ID] for event in e]
        self._viewmodel.set_selected_flow_ids(flow_ids)
        self._viewmodel.refresh_items_on_canvas()

    def build(self) -> Self:
        self._flow_table.build()
        with ui.row().style(BASIC_WIDTH):
            self._button_add = ui.button(
                self._resource_manager.get(FlowKeys.BUTTON_ADD), on_click=self.add_flow
            ).style(BUTTON_WIDTH)
            self._button_add.mark(MARKER_BUTTON_ADD)
            self._button_generate = ui.button(
                self._resource_manager.get(FlowKeys.BUTTON_GENERATE),
                on_click=self.generate_flow,
            ).style(BUTTON_WIDTH)
            self._button_generate.mark(MARKER_BUTTON_GENERATE)

        with ui.row().style(BASIC_WIDTH):
            self._button_remove = ui.button(
                self._resource_manager.get(FlowKeys.BUTTON_REMOVE),
                on_click=self.remove_flow,
            ).style(BUTTON_WIDTH)
            self._button_remove.mark(MARKER_BUTTON_REMOVE)
            self._button_properties = ui.button(
                self._resource_manager.get(FlowKeys.BUTTON_PROPERTIES),
                on_click=self.show_flow_properties,
            ).style(BUTTON_WIDTH)
            self._button_properties.mark(MARKER_BUTTON_PROPERTIES)
        self.update_items()
        return self

    async def add_flow(self, _: ClickEventArguments) -> None:
        await self._viewmodel.add_flow()

    def generate_flow(self) -> None:
        self._viewmodel.generate_flows()

    def remove_flow(self) -> None:
        self._viewmodel.remove_flows()

    async def show_flow_properties(self) -> None:
        await self._viewmodel.edit_selected_flow()

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        pass

    def update_items(self) -> None:
        self._flow_table.update(map_to_ui(self._viewmodel.get_all_flows()))
        selected_flows = [flow.id for flow in self._flow_state.selected_flows.get()]
        self.update_selected_items(selected_flows)

    def update_selected_items(self, item_ids: list[str]) -> None:
        self._flow_table.select(item_ids)

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
        if self._button_properties:
            return [self._button_properties]
        return []

    def get_multiple_items_buttons(self) -> list[Button]:
        if self._button_remove:
            return [self._button_remove]
        return []
