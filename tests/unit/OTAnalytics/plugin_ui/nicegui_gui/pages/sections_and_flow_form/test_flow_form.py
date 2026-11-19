"""Tests editing a flow by double-clicking it in the WebUI flow table."""

import asyncio
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.application.state import FlowState
from OTAnalytics.domain.event import EventRepositoryEvent
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.theme.global_theme import STALE_CLASS
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.flow_form import (
    AUTO_ASSIGNMENT_DELAY,
    COLUMN_TRACKS_ASSIGNED,
    MARKER_AUTO_ASSIGNMENT,
    MARKER_FLOW_TABLE,
    MARKER_UPDATE_FLOW_HIGHLIGHTING,
    FlowForm,
)
from tests.utils.nicegui_table import double_click_row, wait_until_awaited

ENDPOINT_NAME = "/test-flow-form-double-click"
FLOW_ID = "flow-1"
FLOW_ROW = {"id": FLOW_ID, "name": "Flow 1"}


class FakeFlow:
    def __init__(self, flow_id: str, name: str) -> None:
        self.id = flow_id
        self.name = name

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name}


def create_viewmodel() -> MagicMock:
    viewmodel = MagicMock(spec=ViewModel)
    viewmodel.get_all_flows.return_value = [FakeFlow(FLOW_ID, "Flow 1")]
    viewmodel.get_tracks_assigned_to_each_flow.return_value = {}
    viewmodel.get_auto_assignment.return_value = False
    return viewmodel


def create_flow_state() -> MagicMock:
    flow_state = MagicMock(spec=FlowState)
    flow_state.selected_flows = MagicMock()
    flow_state.selected_flows.get.return_value = []
    return flow_state


class TestFlowFormDoubleClick:
    @pytest.mark.asyncio
    async def test_double_click_selects_flow_and_opens_properties(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_viewmodel()
        target = FlowForm(viewmodel, create_flow_state(), resource_manager)

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT_NAME)

        double_click_row(user, MARKER_FLOW_TABLE, FLOW_ROW)
        await wait_until_awaited(viewmodel.edit_selected_flow)

        viewmodel.set_selected_flow_ids.assert_called_with([FLOW_ID])
        viewmodel.edit_selected_flow.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_double_click_does_nothing_while_disabled(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_viewmodel()
        target = FlowForm(viewmodel, create_flow_state(), resource_manager)

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT_NAME)
        target.disable()
        viewmodel.set_selected_flow_ids.reset_mock()

        double_click_row(user, MARKER_FLOW_TABLE, FLOW_ROW)
        await wait_until_awaited(viewmodel.edit_selected_flow)

        viewmodel.set_selected_flow_ids.assert_not_called()
        viewmodel.edit_selected_flow.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_double_click_works_again_after_enable(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_viewmodel()
        target = FlowForm(viewmodel, create_flow_state(), resource_manager)

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT_NAME)
        target.disable()
        target.enable()

        double_click_row(user, MARKER_FLOW_TABLE, FLOW_ROW)
        await wait_until_awaited(viewmodel.edit_selected_flow)

        viewmodel.edit_selected_flow.assert_awaited_once()


AUTO_ENDPOINT = "/test-flow-form-auto-assignment"
SECTION_ID = Mock()
AFTER_DEBOUNCE = AUTO_ASSIGNMENT_DELAY + 0.3


def create_auto_viewmodel(auto: bool) -> MagicMock:
    viewmodel = create_viewmodel()
    viewmodel.get_auto_assignment.return_value = auto
    return viewmodel


async def open_flow_form(
    user: User, viewmodel: MagicMock, resource_manager: ResourceManager
) -> FlowForm:
    target = FlowForm(viewmodel, create_flow_state(), resource_manager)

    @ui.page(AUTO_ENDPOINT)
    def page() -> None:
        target.build()

    await user.open(AUTO_ENDPOINT)
    return target


class TestTrackAssignment:
    async def test_update_now_creates_events(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_auto_viewmodel(auto=False)
        await open_flow_form(user, viewmodel, resource_manager)

        user.find(marker=MARKER_UPDATE_FLOW_HIGHLIGHTING).click()

        viewmodel.create_events.assert_called_once_with()

    async def test_switch_shows_and_sets_the_view_model_state(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_auto_viewmodel(auto=True)
        await open_flow_form(user, viewmodel, resource_manager)
        switch = user.find(marker=MARKER_AUTO_ASSIGNMENT).elements.pop()
        assert isinstance(switch, ui.switch)
        assert switch.value is True

        user.find(marker=MARKER_AUTO_ASSIGNMENT).click()

        viewmodel.set_auto_assignment.assert_called_once_with(False)

    async def test_changes_create_events_once_after_a_pause(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_auto_viewmodel(auto=True)
        target = await open_flow_form(user, viewmodel, resource_manager)

        target.notify_section_changed(SECTION_ID)
        target.notify_flows([])
        target.notify_section_changed(SECTION_ID)
        await asyncio.sleep(AFTER_DEBOUNCE)

        viewmodel.assign_tracks.assert_called_once_with()
        viewmodel.create_events.assert_not_called()

    async def test_loaded_tracks_are_assigned_once_after_a_pause(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        """Loading tracks clears every event, e.g. when a project is opened."""
        viewmodel = create_auto_viewmodel(auto=True)
        target = await open_flow_form(user, viewmodel, resource_manager)

        target.notify_tracks(Mock())
        await asyncio.sleep(AFTER_DEBOUNCE)

        viewmodel.assign_tracks.assert_called_once_with()

    async def test_changes_do_nothing_without_auto_assignment(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_auto_viewmodel(auto=False)
        target = await open_flow_form(user, viewmodel, resource_manager)

        target.notify_section_changed(SECTION_ID)
        target.notify_flows([])
        await asyncio.sleep(AFTER_DEBOUNCE)

        viewmodel.assign_tracks.assert_not_called()

    async def test_changes_without_flows_do_nothing(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_auto_viewmodel(auto=True)
        target = await open_flow_form(user, viewmodel, resource_manager)
        viewmodel.get_all_flows.return_value = []

        target.notify_flows([])
        await asyncio.sleep(AFTER_DEBOUNCE)

        viewmodel.assign_tracks.assert_not_called()

    def test_changes_before_build_do_nothing(
        self, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_auto_viewmodel(auto=True)
        target = FlowForm(viewmodel, create_flow_state(), resource_manager)

        target.notify_section_changed(SECTION_ID)

        viewmodel.assign_tracks.assert_not_called()


def tracks_column_classes(user: User) -> str:
    table = user.find(marker=MARKER_FLOW_TABLE).elements.pop()
    assert isinstance(table, ui.table)
    column = next(c for c in table.columns if c["name"] == COLUMN_TRACKS_ASSIGNED)
    return str(column.get("classes", ""))


class TestOutdatedAssignment:
    async def test_changes_mark_the_assignment_outdated(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_auto_viewmodel(auto=False)
        target = await open_flow_form(user, viewmodel, resource_manager)
        observer = Mock()
        target.register_outdated_observer(observer)

        target.notify_section_changed(SECTION_ID)

        observer.assert_called_once_with(True)
        assert STALE_CLASS in tracks_column_classes(user)

    async def test_update_now_marks_the_assignment_up_to_date(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_auto_viewmodel(auto=False)
        target = await open_flow_form(user, viewmodel, resource_manager)
        observer = Mock()
        target.register_outdated_observer(observer)
        target.notify_flows([])

        user.find(marker=MARKER_UPDATE_FLOW_HIGHLIGHTING).click()

        assert observer.call_args_list[-1].args == (False,)
        assert STALE_CLASS not in tracks_column_classes(user)

    async def test_automatic_assignment_marks_it_up_to_date(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_auto_viewmodel(auto=True)
        target = await open_flow_form(user, viewmodel, resource_manager)

        target.notify_section_changed(SECTION_ID)
        assert target.is_outdated()
        await asyncio.sleep(AFTER_DEBOUNCE)

        assert not target.is_outdated()

    async def test_changes_before_build_are_assigned_once_built(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        """E.g. a project preloaded from the command line."""
        viewmodel = create_auto_viewmodel(auto=True)
        target = FlowForm(viewmodel, create_flow_state(), resource_manager)
        target.notify_flows([])

        @ui.page(AUTO_ENDPOINT)
        def page() -> None:
            target.build()

        await user.open(AUTO_ENDPOINT)
        await asyncio.sleep(AFTER_DEBOUNCE)

        viewmodel.assign_tracks.assert_called_once_with()
        assert not target.is_outdated()

    async def test_changed_tracks_mark_the_assignment_outdated(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_auto_viewmodel(auto=False)
        target = await open_flow_form(user, viewmodel, resource_manager)

        target.notify_tracks(Mock())

        assert target.is_outdated()

    async def test_added_events_mark_the_assignment_up_to_date(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        """Assigned elsewhere, e.g. by an export."""
        viewmodel = create_auto_viewmodel(auto=False)
        target = await open_flow_form(user, viewmodel, resource_manager)
        target.notify_section_changed(SECTION_ID)

        target.notify_events(EventRepositoryEvent([Mock()], []))

        assert not target.is_outdated()

    async def test_assignment_without_events_marks_it_up_to_date(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        """No track intersects a section, so no event is added."""
        viewmodel = create_auto_viewmodel(auto=False)
        target = await open_flow_form(user, viewmodel, resource_manager)
        target.notify_section_changed(SECTION_ID)

        target.notify_events(EventRepositoryEvent([], []))

        assert not target.is_outdated()

    async def test_removed_events_keep_the_assignment_outdated(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_auto_viewmodel(auto=False)
        target = await open_flow_form(user, viewmodel, resource_manager)
        target.notify_section_changed(SECTION_ID)

        target.notify_events(EventRepositoryEvent([], [Mock()]))

        assert target.is_outdated()
