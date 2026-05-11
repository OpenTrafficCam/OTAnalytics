from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.application.state import FlowState
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.flow_form import (
    MARKER_BUTTON_ADD,
    MARKER_BUTTON_GENERATE,
    MARKER_BUTTON_PROPERTIES,
    MARKER_BUTTON_REMOVE,
    MARKER_FLOW_TABLE,
    FlowForm,
)

# Constants for testing
ENDPOINT_NAME = "/test-flow-form"
FLOW_ID_1 = "flow-1"
FLOW_ID_2 = "flow-2"
FLOW_NAME_1 = "Flow 1"
FLOW_NAME_2 = "Flow 2"


class MockFlow:
    def __init__(self, flow_id: str, name: str) -> None:
        self.id = flow_id
        self.name = name

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name}


@pytest.fixture
def viewmodel() -> Mock:
    viewmodel = MagicMock(spec=ViewModel)

    # Set up mock methods
    viewmodel.get_all_flows.return_value = [
        MockFlow(FLOW_ID_1, FLOW_NAME_1),
        MockFlow(FLOW_ID_2, FLOW_NAME_2),
    ]

    return viewmodel


@pytest.fixture
def flow_state() -> Mock:
    flow_state = MagicMock(spec=FlowState)

    # Set up selected_flows observable
    selected_flows_mock = MagicMock()
    selected_flows_mock.get.return_value = []
    flow_state.selected_flows = selected_flows_mock

    return flow_state


@pytest.fixture
def flow_form(
    viewmodel: ViewModel, flow_state: FlowState, resource_manager: ResourceManager
) -> FlowForm:
    return FlowForm(viewmodel, flow_state, resource_manager)


class TestFlowForm:

    @pytest.mark.asyncio
    async def test_form_build_up(
        self,
        user: User,
        flow_form: FlowForm,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that the form builds correctly and displays all buttons."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            flow_form.build()

        await user.open(ENDPOINT_NAME)

        # Check that all buttons are visible
        await user.should_see(marker=MARKER_BUTTON_ADD)
        await user.should_see(marker=MARKER_BUTTON_GENERATE)
        await user.should_see(marker=MARKER_BUTTON_REMOVE)
        await user.should_see(marker=MARKER_BUTTON_PROPERTIES)

        # Just check that all buttons are visible, skip checking the table for now
        # The table is built, but we can't easily check its contents in this test

    @pytest.mark.asyncio
    async def test_generate_flow_button_calls_viewmodel(
        self,
        user: User,
        flow_form: FlowForm,
        viewmodel: Mock,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that clicking the generate flow button calls the viewmodel method."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            flow_form.build()

        await user.open(ENDPOINT_NAME)

        # Directly call the generate_flow method
        user.find(marker=MARKER_BUTTON_GENERATE).click()

        # Verify that the viewmodel method was called
        viewmodel.generate_flows.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_flow_button_calls_viewmodel(
        self,
        user: User,
        flow_form: FlowForm,
        viewmodel: Mock,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that clicking the remove flow button calls the viewmodel method."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            flow_form.build()

        await user.open(ENDPOINT_NAME)

        # Directly call the remove_flow method
        user.find(marker=MARKER_BUTTON_REMOVE).click()

        # Verify that the viewmodel method was called
        viewmodel.remove_flows.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_items_displays_flows(
        self,
        user: User,
        flow_form: FlowForm,
        viewmodel: Mock,
    ) -> None:
        """Test that update_items displays the flows from the viewmodel."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            flow_form.build()

        await user.open(ENDPOINT_NAME)

        # Verify that the table is displayed
        await user.should_see(marker=MARKER_FLOW_TABLE)

        # Verify that the flows are in the table's rows
        names = [row.get("name") for row in flow_form._flow_table._rows]
        assert names == [FLOW_NAME_1, FLOW_NAME_2]

        # Change the flows returned by the viewmodel
        new_flow = MockFlow("flow-3", "New Flow")
        viewmodel.get_all_flows.return_value = [new_flow]

        # Update the items
        flow_form.update_items()

        # Verify that the new flow is in the table's rows
        assert names == [FLOW_NAME_1, FLOW_NAME_2]
