from unittest.mock import MagicMock, Mock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.flow_dto import FlowDto
from OTAnalytics.adapter_ui.text_resources import ColumnResources
from OTAnalytics.application.use_cases.generate_flows import FlowNameGenerator
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.edit_flow_dialog import (
    MARKER_DISTANCE,
    MARKER_END_SECTION,
    MARKER_NAME,
    MARKER_START_SECTION,
    EditFlowDialog,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import (
    MARKER_APPLY,
    MARKER_CANCEL,
)

# Constants for testing
TEST_FLOW_NAME = "Test Flow"
TEST_START_SECTION = "Section A"
TEST_END_SECTION = "Section B"
TEST_START_SECTION_ID = "section-a-id"
TEST_END_SECTION_ID = "section-b-id"
TEST_DISTANCE = 100.0
TEST_FLOW_ID = "flow-123"
ENDPOINT_NAME = "/test-edit-flow-dialog"


@pytest.fixture
def section_ids() -> Mock:
    section_ids = MagicMock(spec=ColumnResources)
    section_ids.names = [TEST_START_SECTION, TEST_END_SECTION, "Section C"]
    # Mock name-to-ID mapping (what the dialog now uses)
    section_ids.get_id_for.side_effect = lambda name: {
        TEST_START_SECTION: TEST_START_SECTION_ID,
        TEST_END_SECTION: TEST_END_SECTION_ID,
        "Section C": "section-c-id",
    }.get(name, name)
    # Mock ID-to-name mapping (for display purposes)
    section_ids.get_name_for.side_effect = lambda id: {
        TEST_START_SECTION_ID: TEST_START_SECTION,
        TEST_END_SECTION_ID: TEST_END_SECTION,
        "section-c-id": "Section C",
    }.get(id, id)
    return section_ids


@pytest.fixture
def name_generator() -> Mock:
    name_generator = MagicMock(spec=FlowNameGenerator)
    # Return the test flow name to avoid auto-generation overriding our test values
    name_generator.generate_from_string.return_value = TEST_FLOW_NAME
    return name_generator


@pytest.fixture
def flow_dto() -> FlowDto:
    return FlowDto(
        name=TEST_FLOW_NAME,
        start_section=TEST_START_SECTION_ID,  # Use section ID, not name
        end_section=TEST_END_SECTION_ID,  # Use section ID, not name
        flow_id=TEST_FLOW_ID,
        distance=TEST_DISTANCE,
    )


@pytest.fixture
def edit_flow_dialog(
    resource_manager: Mock, section_ids: Mock, name_generator: Mock
) -> EditFlowDialog:
    return EditFlowDialog(
        resource_manager=resource_manager,
        section_ids=section_ids,
        name_generator=name_generator,
    )


@pytest.fixture
def edit_flow_dialog_with_input(
    resource_manager: Mock, section_ids: Mock, name_generator: Mock, flow_dto: FlowDto
) -> EditFlowDialog:
    return EditFlowDialog(
        resource_manager=resource_manager,
        section_ids=section_ids,
        name_generator=name_generator,
        input_values=flow_dto,
    )


class TestEditFlowDialog:
    @pytest.mark.asyncio
    async def test_dialog_build_up(
        self,
        user: User,
        edit_flow_dialog: EditFlowDialog,
    ) -> None:
        """Test that the dialog builds up correctly and all elements are visible."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            edit_flow_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Check that all elements are visible
        await user.should_see(marker=MARKER_NAME)
        await user.should_see(marker=MARKER_START_SECTION)
        await user.should_see(marker=MARKER_END_SECTION)
        await user.should_see(marker=MARKER_DISTANCE)
        await user.should_see(marker=MARKER_APPLY)
        await user.should_see(marker=MARKER_CANCEL)

    @pytest.mark.asyncio
    async def test_dialog_with_input_values(
        self,
        user: User,
        edit_flow_dialog_with_input: EditFlowDialog,
    ) -> None:
        """Test that the dialog initializes correctly with input values."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            edit_flow_dialog_with_input.build().open()

        await user.open(ENDPOINT_NAME)

        # Check that the input values are correctly set
        assert edit_flow_dialog_with_input._name.value == TEST_FLOW_NAME
        assert edit_flow_dialog_with_input._start_section.value == TEST_START_SECTION
        assert edit_flow_dialog_with_input._end_section.value == TEST_END_SECTION
        assert edit_flow_dialog_with_input._distance.value == TEST_DISTANCE

    @pytest.mark.asyncio
    async def test_get_flow(
        self,
        user: User,
        edit_flow_dialog: EditFlowDialog,
    ) -> None:
        """Test that get_flow returns the correct flow."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            edit_flow_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Set values using the user fixture
        user.find(marker=MARKER_NAME).clear().type(TEST_FLOW_NAME)
        user.find(marker=MARKER_START_SECTION).click()
        user.find(TEST_START_SECTION).click()
        user.find(marker=MARKER_END_SECTION).click()
        user.find(TEST_END_SECTION).click()

        # Set distance value
        # Note: We can't use user.find(marker=MARKER_DISTANCE).clear().type() here
        # ui.number elements don't support these methods in the testing framework.
        # Instead, we set the value directly on the dialog instance.
        edit_flow_dialog._distance.set_value(TEST_DISTANCE)

        user.find(marker=MARKER_APPLY).click()

        # Get the flow
        flow = edit_flow_dialog.get_flow()

        # Check that the flow has the correct values
        assert flow.name == TEST_FLOW_NAME
        assert (
            flow.start_section == TEST_START_SECTION_ID
        )  # Now expects section ID, not name
        assert (
            flow.end_section == TEST_END_SECTION_ID
        )  # Now expects section ID, not name
        assert flow.distance == TEST_DISTANCE
        assert flow.flow_id is None  # No input values were provided

    @pytest.mark.asyncio
    async def test_get_flow_with_input_values(
        self,
        user: User,
        edit_flow_dialog_with_input: EditFlowDialog,
    ) -> None:
        """Test that get_flow returns the correct flow with input values."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            edit_flow_dialog_with_input.build().open()

        await user.open(ENDPOINT_NAME)

        # Get the flow without changing anything
        flow = edit_flow_dialog_with_input.get_flow()

        # Check that the flow has the correct values
        assert flow.name == TEST_FLOW_NAME
        assert (
            flow.start_section == TEST_START_SECTION_ID
        )  # Now expects section ID, not name
        assert (
            flow.end_section == TEST_END_SECTION_ID
        )  # Now expects section ID, not name
        assert flow.distance == TEST_DISTANCE
        assert flow.flow_id == TEST_FLOW_ID

    @pytest.mark.asyncio
    async def test_auto_name_generation(
        self,
        user: User,
        edit_flow_dialog: EditFlowDialog,
        name_generator: Mock,
    ) -> None:
        """Test that the name is automatically generated when sections change."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            edit_flow_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Set start and end sections using the user fixture
        user.find(marker=MARKER_START_SECTION).click()
        user.find(TEST_START_SECTION).click()
        user.find(marker=MARKER_END_SECTION).click()
        user.find(TEST_END_SECTION).click()

        # Check that name_generator was called with the correct arguments
        name_generator.generate_from_string.assert_called_with(
            TEST_START_SECTION, TEST_END_SECTION
        )

        # Check that the name was updated
        assert edit_flow_dialog._name.value == TEST_FLOW_NAME
