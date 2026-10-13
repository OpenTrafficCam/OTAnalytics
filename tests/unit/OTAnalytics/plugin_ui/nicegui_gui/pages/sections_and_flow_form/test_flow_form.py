"""Tests editing a flow by double-clicking it in the WebUI flow table."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.application.state import FlowState
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.flow_form import (
    MARKER_FLOW_TABLE,
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
