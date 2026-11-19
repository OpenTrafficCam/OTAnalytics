from typing import Any, Callable, Iterable, Mapping, Self

from nicegui import ui
from nicegui.elements.button import Button
from nicegui.events import ClickEventArguments

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import FlowKeys, ResourceManager
from OTAnalytics.application.state import FlowState
from OTAnalytics.domain.event import EventRepositoryEvent
from OTAnalytics.domain.flow import FLOW_NAME, Flow, FlowId, FlowListObserver
from OTAnalytics.domain.section import SectionId
from OTAnalytics.domain.track_repository import TrackListObserver, TrackRepositoryEvent
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import (
    COLUMN_ID,
    CustomTable,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.theme.global_theme import STALE_CLASS
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID
from OTAnalytics.plugin_ui.utils.asyncio_helper import run_async

BUTTON_ROW = "ota-button-row"
MARKER_FLOW_TABLE = "marker-flow-table"
MARKER_BUTTON_ADD = "marker-button-add"
MARKER_BUTTON_GENERATE = "marker-button-generate"
MARKER_BUTTON_REMOVE = "marker-button-remove"
MARKER_BUTTON_PROPERTIES = "marker-button-properties"
MARKER_UPDATE_FLOW_HIGHLIGHTING = "marker-update-flow-highlighting"
MARKER_AUTO_ASSIGNMENT = "marker-auto-assignment"
AUTO_ASSIGNMENT_DELAY = 0.5
"""Seconds without changes before tracks are assigned, so drawing several
sections in a row triggers one assignment."""
COLUMN_TRACKS_ASSIGNED = "tracks_assigned"


def create_columns(
    resource_manager: ResourceManager, outdated: bool = False
) -> list[dict[str, str]]:
    """Columns of the flow table; outdated track counts are dimmed."""
    tracks_assigned = {
        "name": COLUMN_TRACKS_ASSIGNED,
        "label": resource_manager.get(FlowKeys.TABLE_COLUMN_TRACKS_ASSIGNED),
        "field": COLUMN_TRACKS_ASSIGNED,
    }
    if outdated:
        tracks_assigned["classes"] = STALE_CLASS
    return [
        {
            "name": FLOW_NAME,
            "label": resource_manager.get(FlowKeys.TABLE_COLUMN_NAME),
            "field": "name",
        },
        tracks_assigned,
    ]


def map_to_ui(
    flows: Iterable[Flow], tracks_assigned_to_each_flow: Mapping[FlowId, int]
) -> list:
    """Map flows to table rows including the number of assigned tracks.

    Flows without an entry in `tracks_assigned_to_each_flow` are shown with 0
    assigned tracks.
    """
    list_of_flows = []
    for flow in flows:
        row = flow.to_dict()
        row[COLUMN_TRACKS_ASSIGNED] = tracks_assigned_to_each_flow.get(flow.id, 0)
        list_of_flows.append(row)
    return list_of_flows


class FlowForm(
    ButtonForm,
    AbstractFrame,
    AbstractTreeviewInterface,
    FlowListObserver,
    TrackListObserver,
):
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
            selection="multiple",
            marker=MARKER_FLOW_TABLE,
            # Let the table auto-select the row on click and forward selection
            auto_select_on_row_click=True,
            on_row_double_click_method=self._edit_flow,
        )
        self._disabled = False
        self._button_remove: ui.button | None = None
        self._button_add: ui.button | None = None
        self._button_generate: ui.button | None = None
        self._button_properties: ui.button | None = None
        self._assignment_row: ui.row | None = None
        self._assignment_timer: ui.timer | None = None
        self._outdated = False
        self._outdated_observers: list[Callable[[bool], None]] = []
        self._introduce_to_viewmodel()

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_flows_frame(self)
        self._viewmodel.set_treeview_flows(self)

    def _select_flow(self, e: list[dict[str, Any]]) -> None:
        flow_ids = [event[COLUMN_ID] for event in e]
        self._viewmodel.set_selected_flow_ids(flow_ids)
        self._viewmodel.refresh_items_on_canvas()

    async def _edit_flow(self, row: dict[str, Any]) -> None:
        if self._disabled:
            return
        self._select_flow([row])
        await self._viewmodel.edit_selected_flow()

    def build(self) -> Self:
        self._flow_table.build()
        with ui.row().classes(BUTTON_ROW):
            self._button_add = ui.button(
                self._resource_manager.get(FlowKeys.BUTTON_ADD), on_click=self.add_flow
            )
            self._button_add.mark(MARKER_BUTTON_ADD)
            self._button_add.props(f"{TEST_ID}={MARKER_BUTTON_ADD}")
            self._button_generate = ui.button(
                self._resource_manager.get(FlowKeys.BUTTON_GENERATE),
                on_click=self.generate_flow,
            )
            self._button_generate.mark(MARKER_BUTTON_GENERATE)
            self._button_generate.props(f"{TEST_ID}={MARKER_BUTTON_GENERATE}")

        with ui.row().classes(BUTTON_ROW):
            self._button_remove = ui.button(
                self._resource_manager.get(FlowKeys.BUTTON_REMOVE),
                on_click=self.remove_flow,
            )
            self._button_remove.mark(MARKER_BUTTON_REMOVE)
            self._button_remove.props(f"{TEST_ID}={MARKER_BUTTON_REMOVE}")
            self._button_properties = ui.button(
                self._resource_manager.get(FlowKeys.BUTTON_PROPERTIES),
                on_click=self.show_flow_properties,
            )
            self._button_properties.mark(MARKER_BUTTON_PROPERTIES)
            self._button_properties.props(f"{TEST_ID}={MARKER_BUTTON_PROPERTIES}")
        self._build_track_assignment()
        self.update_items()
        if self._outdated:
            # Changed before there was a page, e.g. by a preloaded project.
            self._schedule_assignment()
        # Buttons did not exist on first introduction, apply their states now
        self._viewmodel.set_flows_frame(self)
        return self

    def _build_track_assignment(self) -> None:
        ui.label(self._resource_manager.get(FlowKeys.LABEL_TRACK_ASSIGNMENT)).classes(
            "text-subtitle2"
        )
        with ui.row().classes("w-full items-center") as self._assignment_row:
            switch = ui.switch(
                self._resource_manager.get(FlowKeys.SWITCH_AUTO_ASSIGNMENT),
                value=self._viewmodel.get_auto_assignment(),
                on_change=lambda event: self._viewmodel.set_auto_assignment(
                    event.value
                ),
            )
            switch.mark(MARKER_AUTO_ASSIGNMENT)
            switch.props(f"{TEST_ID}={MARKER_AUTO_ASSIGNMENT}")
            button = ui.button(
                self._resource_manager.get(FlowKeys.BUTTON_UPDATE_ASSIGNMENT),
                on_click=self.update_assignment,
            )
            button.mark(MARKER_UPDATE_FLOW_HIGHLIGHTING)
            button.props(f"{TEST_ID}={MARKER_UPDATE_FLOW_HIGHLIGHTING}")

    def register_outdated_observer(self, observer: Callable[[bool], None]) -> None:
        """Listen to whether the track assignment is out of date."""
        self._outdated_observers.append(observer)

    def is_outdated(self) -> bool:
        return self._outdated

    def update_assignment(self) -> None:
        """Assign the tracks to the flows now."""
        self._viewmodel.create_events()
        self._set_outdated(False)

    def notify_section_changed(self, _: SectionId) -> None:
        self._on_assignment_input_changed()

    def _on_assignment_input_changed(self) -> None:
        """Without flows there is no assignment that could be out of date."""
        self._set_outdated(bool(self._viewmodel.get_all_flows()))
        self._schedule_assignment()

    def _set_outdated(self, outdated: bool) -> None:
        if outdated == self._outdated:
            return
        self._outdated = outdated
        self._flow_table.update_columns(
            create_columns(self._resource_manager, outdated)
        )
        for observer in self._outdated_observers:
            observer(outdated)

    def notify_tracks(self, _: TrackRepositoryEvent) -> None:
        """Changed tracks clear every event, e.g. when a project is opened."""
        self._on_assignment_input_changed()

    def _schedule_assignment(self) -> None:
        """Assign the tracks once the changes pause, if automatic assignment is on.

        Without a built page there is nobody to show the assignment to.
        """
        if (
            self._assignment_row is None
            or not self._viewmodel.get_auto_assignment()
            or not self._viewmodel.get_all_flows()
        ):
            return
        if self._assignment_timer is not None:
            self._assignment_timer.cancel()
        with self._assignment_row:
            self._assignment_timer = ui.timer(
                AUTO_ASSIGNMENT_DELAY, self._assign_tracks, once=True
            )

    def _assign_tracks(self) -> None:
        self._assignment_timer = None
        if self._viewmodel.get_auto_assignment():
            self._viewmodel.assign_tracks()
            self._set_outdated(False)

    async def add_flow(self, _: ClickEventArguments) -> None:
        await self._viewmodel.add_flow()

    def generate_flow(self) -> None:
        self._viewmodel.generate_flows()

    def remove_flow(self) -> None:
        run_async(self._viewmodel.remove_flows())

    async def show_flow_properties(self) -> None:
        await self._viewmodel.edit_selected_flow()

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        pass

    def notify_flows(self, flows: list[FlowId]) -> None:
        """Refresh the table after flows changed.

        Must be called after the road user assignments of the changed flows have
        been cleared, so the number of assigned tracks is up to date.
        """
        self.update_items()
        self._on_assignment_input_changed()

    def notify_events(self, _: EventRepositoryEvent) -> None:
        """Refresh the number of assigned tracks after events changed."""
        self.update_items()

    def update_items(self) -> None:
        self._flow_table.update(
            map_to_ui(
                self._viewmodel.get_all_flows(),
                self._viewmodel.get_tracks_assigned_to_each_flow(),
            )
        )
        selected_flows = [flow.id for flow in self._flow_state.selected_flows.get()]
        self.update_selected_items(selected_flows)

    def update_selected_items(self, item_ids: list[str]) -> None:
        self._flow_table.select(item_ids)

    def enable(self) -> None:
        self._disabled = False
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
        self._disabled = True
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
        if self._button_add and self._button_generate:
            return [self._button_add, self._button_generate]
        return []

    def get_single_item_buttons(self) -> list[Button]:
        if self._button_properties:
            return [self._button_properties]
        return []

    def get_multiple_items_buttons(self) -> list[Button]:
        if self._button_remove:
            return [self._button_remove]
        return []

    def _set_enabled_buttons(self, buttons: list[Button], enabled: bool) -> None:
        super()._set_enabled_buttons(buttons, enabled)
        if self._button_generate and len(list(self._viewmodel.get_all_flows())) > 0:
            self._button_generate.disable()
