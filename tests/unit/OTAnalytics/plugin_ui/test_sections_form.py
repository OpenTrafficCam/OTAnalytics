from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.application.state import SectionState
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.sections_form import (  # noqa
    MARKER_BUTTON_ADD_AREA,
    MARKER_BUTTON_ADD_LINE,
    MARKER_BUTTON_EDIT,
    MARKER_BUTTON_PROPERTIES,
    MARKER_BUTTON_REMOVE,
    MARKER_SECTION_TABLE,
    SectionsForm,
)

# Constants for testing
ENDPOINT_NAME = "/test-sections-form"
SECTION_ID_1 = "section-1"
SECTION_ID_2 = "section-2"
SECTION_NAME_1 = "Section 1"
SECTION_NAME_2 = "Section 2"


class MockSection:
    def __init__(self, section_id: str, name: str) -> None:
        self.id = section_id
        self.name = name

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name}


@pytest.fixture
def viewmodel() -> Mock:
    viewmodel = MagicMock(spec=ViewModel)

    # Set up mock methods
    viewmodel.get_all_sections.return_value = [
        MockSection(SECTION_ID_1, SECTION_NAME_1),
        MockSection(SECTION_ID_2, SECTION_NAME_2),
    ]

    return viewmodel


@pytest.fixture
def section_state() -> Mock:
    section_state = MagicMock(spec=SectionState)

    # Set up selected_sections observable
    selected_sections_mock = MagicMock()
    selected_sections_mock.get.return_value = []
    section_state.selected_sections = selected_sections_mock

    return section_state


@pytest.fixture
def sections_form(
    viewmodel: ViewModel, section_state: SectionState, resource_manager: ResourceManager
) -> SectionsForm:
    return SectionsForm(viewmodel, section_state, resource_manager)


class TestSectionsForm:

    @pytest.mark.asyncio
    async def test_form_build_up(
        self,
        user: User,
        sections_form: SectionsForm,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that the form builds correctly and displays all buttons."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            sections_form.build()

        await user.open(ENDPOINT_NAME)

        # Check that all buttons are visible
        await user.should_see(marker=MARKER_BUTTON_ADD_LINE)
        await user.should_see(marker=MARKER_BUTTON_ADD_AREA)
        await user.should_see(marker=MARKER_BUTTON_EDIT)
        await user.should_see(marker=MARKER_BUTTON_PROPERTIES)
        await user.should_see(marker=MARKER_BUTTON_REMOVE)

    @pytest.mark.asyncio
    async def test_add_line_section_button_calls_viewmodel(
        self,
        user: User,
        sections_form: SectionsForm,
        viewmodel: Mock,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that clicking the add line section button calls the viewmodel method."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            sections_form.build()

        await user.open(ENDPOINT_NAME)

        # Click the add line section button
        user.find(marker=MARKER_BUTTON_ADD_LINE).click()

        # Verify that the viewmodel method was called
        viewmodel.add_line_section.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_area_section_button_calls_viewmodel(
        self,
        user: User,
        sections_form: SectionsForm,
        viewmodel: Mock,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that clicking the add area section button calls the viewmodel method."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            sections_form.build()

        await user.open(ENDPOINT_NAME)

        # Click the add area section button
        user.find(marker=MARKER_BUTTON_ADD_AREA).click()

        # Verify that the viewmodel method was called
        viewmodel.add_area_section.assert_called_once()

    @pytest.mark.asyncio
    async def test_edit_section_button_calls_viewmodel(
        self,
        user: User,
        sections_form: SectionsForm,
        viewmodel: Mock,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that clicking the edit section button calls the viewmodel method."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            sections_form.build()

        await user.open(ENDPOINT_NAME)

        # Click the edit section button
        user.find(marker=MARKER_BUTTON_EDIT).click()

        # Verify that the viewmodel method was called
        viewmodel.edit_section_geometry.assert_called_once()

    @pytest.mark.asyncio
    async def test_properties_button_calls_viewmodel(
        self,
        user: User,
        sections_form: SectionsForm,
        viewmodel: Mock,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that clicking the properties button calls the viewmodel method."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            sections_form.build()

        await user.open(ENDPOINT_NAME)

        # Click the properties button
        user.find(marker=MARKER_BUTTON_PROPERTIES).click()

        # Verify that the viewmodel method was called
        viewmodel.edit_selected_section_metadata.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_section_button_calls_viewmodel(
        self,
        user: User,
        sections_form: SectionsForm,
        viewmodel: Mock,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that clicking the remove section button calls the viewmodel method."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            sections_form.build()

        await user.open(ENDPOINT_NAME)

        # Click the remove section button
        user.find(marker=MARKER_BUTTON_REMOVE).click()

        # Verify that the viewmodel method was called
        viewmodel.remove_sections.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_items_displays_sections(
        self,
        user: User,
        sections_form: SectionsForm,
        viewmodel: Mock,
    ) -> None:
        """Test that update_items displays the sections from the viewmodel."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            sections_form.build()

        await user.open(ENDPOINT_NAME)
        # Change the sections returned by the viewmodel
        new_section = MockSection("section-3", "New Section")
        viewmodel.get_all_sections.return_value = [new_section]

        # Update the items
        sections_form.update_items()

        # Verify that the table is displayed
        await user.should_see(marker=MARKER_SECTION_TABLE)

        # Verify that the new section is in the table's rows
        assert any(
            row.get("name") == "New Section"
            for row in sections_form._section_table._rows
        )

    @pytest.mark.asyncio
    async def test_select_section_updates_viewmodel(
        self,
        user: User,
        sections_form: SectionsForm,
        viewmodel: Mock,
    ) -> None:
        """Test that selecting a section updates the viewmodel."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            sections_form.build()

        await user.open(ENDPOINT_NAME)

        # Directly call the _select_section method with a mock selection event
        sections_form._select_section(
            [{"id": SECTION_ID_1}]
        )  # TODO Refaktor Table tests

        # Verify that the viewmodel method was called with the correct section ID
        viewmodel.set_selected_section_ids.assert_called()
        # Note: We can't easily verify the exact arguments because the selection event
        # is handled internally by the table component
