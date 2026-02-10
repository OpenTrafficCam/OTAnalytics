from unittest.mock import MagicMock, Mock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.domain.section import NAME, RELATIVE_OFFSET_COORDINATES
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_sections import (
    NoUniqueNameException,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.edit_section_dialog import (
    MARKER_NAME,
    EditSectionDialog,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import (
    MARKER_APPLY,
    MARKER_CANCEL,
)

# Constants for testing
TEST_SECTION_NAME = "Test Section"
TEST_TITLE = "Edit Section"
TEST_OFFSET_X = 0.5
TEST_OFFSET_Y = 0.5
ENDPOINT_NAME = "/test-edit-section-dialog"


@pytest.fixture
def section_offset() -> RelativeOffsetCoordinate:
    return RelativeOffsetCoordinate(x=TEST_OFFSET_X, y=TEST_OFFSET_Y)


@pytest.fixture
def input_values() -> dict:
    return {
        NAME: TEST_SECTION_NAME,
        RELATIVE_OFFSET_COORDINATES: {
            EventType.SECTION_ENTER.serialize(): {
                "x": TEST_OFFSET_X,
                "y": TEST_OFFSET_Y,
            }
        },
    }


@pytest.fixture
def viewmodel() -> Mock:
    viewmodel = MagicMock(spec=ViewModel)
    viewmodel.is_section_name_valid.return_value = True
    return viewmodel


@pytest.fixture
def edit_section_dialog(
    resource_manager: Mock, viewmodel: Mock, section_offset: RelativeOffsetCoordinate
) -> EditSectionDialog:
    return EditSectionDialog(
        resource_manager=resource_manager,
        viewmodel=viewmodel,
        title=TEST_TITLE,
        section_offset=section_offset,
    )


@pytest.fixture
def edit_section_dialog_with_input(
    resource_manager: Mock,
    viewmodel: Mock,
    section_offset: RelativeOffsetCoordinate,
    input_values: dict,
) -> EditSectionDialog:
    return EditSectionDialog(
        resource_manager=resource_manager,
        viewmodel=viewmodel,
        title=TEST_TITLE,
        section_offset=section_offset,
        input_values=input_values,
    )


class TestEditSectionDialog:
    @pytest.mark.asyncio
    async def test_dialog_build_up(
        self,
        user: User,
        edit_section_dialog: EditSectionDialog,
    ) -> None:
        """Test that the dialog builds up correctly and all elements are visible."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            edit_section_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Check that all elements are visible
        await user.should_see(marker=MARKER_NAME)
        await user.should_see(marker=MARKER_APPLY)
        await user.should_see(marker=MARKER_CANCEL)

    @pytest.mark.asyncio
    async def test_dialog_with_input_values(
        self,
        user: User,
        edit_section_dialog_with_input: EditSectionDialog,
    ) -> None:
        """Test that the dialog initializes correctly with input values."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            edit_section_dialog_with_input.build().open()

        await user.open(ENDPOINT_NAME)

        # Check that the input values are correctly set
        assert edit_section_dialog_with_input._name.value == TEST_SECTION_NAME

    @pytest.mark.asyncio
    async def test_get_section(
        self,
        user: User,
        edit_section_dialog: EditSectionDialog,
        viewmodel: Mock,
    ) -> None:
        """Test that get_section returns the correct section."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            edit_section_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Set values
        user.find(MARKER_NAME).type(TEST_SECTION_NAME)
        user.find(marker=MARKER_APPLY).click()

        # Get the section
        section = edit_section_dialog.get_section()

        # Check that the section has the correct values
        assert section[NAME] == TEST_SECTION_NAME
        assert (
            EventType.SECTION_ENTER.serialize() in section[RELATIVE_OFFSET_COORDINATES]
        )

        # Check that viewmodel.is_section_name_valid was called
        viewmodel.is_section_name_valid.assert_called_with(TEST_SECTION_NAME)

    @pytest.mark.asyncio
    async def test_get_section_with_input_values(
        self,
        user: User,
        edit_section_dialog_with_input: EditSectionDialog,
    ) -> None:
        """Test that get_section returns the correct section with input values."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            edit_section_dialog_with_input.build().open()

        await user.open(ENDPOINT_NAME)

        # Get the section without changing anything
        section = edit_section_dialog_with_input.get_section()

        # Check that the section has the correct values
        assert section[NAME] == TEST_SECTION_NAME
        assert (
            EventType.SECTION_ENTER.serialize() in section[RELATIVE_OFFSET_COORDINATES]
        )

    @pytest.mark.asyncio
    async def test_name_validation_error(
        self,
        user: User,
        edit_section_dialog: EditSectionDialog,
        viewmodel: Mock,
    ) -> None:
        """Test that validation errors are handled correctly for non-unique names."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            edit_section_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Set a name that will fail validation
        viewmodel.is_section_name_valid.return_value = False
        user.find(MARKER_NAME).type("Duplicate Name")
        user.find(marker=MARKER_APPLY).click()

        # Verify that get_section raises a NoUniqueNameException
        with pytest.raises(NoUniqueNameException):
            edit_section_dialog.get_section()
