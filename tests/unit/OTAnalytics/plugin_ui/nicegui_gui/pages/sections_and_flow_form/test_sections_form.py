"""Tests editing a section by double-clicking it in the WebUI section table."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.application.state import SectionState
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.sections_form import (  # noqa
    MARKER_SECTION_TABLE,
    SectionsForm,
)
from tests.utils.nicegui_table import double_click_row, wait_until_awaited

ENDPOINT_NAME = "/test-sections-form-double-click"
SECTION_ID = "section-1"
SECTION_ROW = {"id": SECTION_ID, "name": "Section 1"}


class FakeSection:
    def __init__(self, section_id: str, name: str) -> None:
        self.id = section_id
        self.name = name

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name}


def create_viewmodel() -> MagicMock:
    viewmodel = MagicMock(spec=ViewModel)
    viewmodel.get_all_sections.return_value = [FakeSection(SECTION_ID, "Section 1")]
    return viewmodel


def create_section_state() -> MagicMock:
    section_state = MagicMock(spec=SectionState)
    section_state.selected_sections = MagicMock()
    section_state.selected_sections.get.return_value = []
    return section_state


class TestSectionsFormDoubleClick:

    @pytest.mark.asyncio
    async def test_double_click_selects_section_and_opens_properties(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_viewmodel()
        target = SectionsForm(viewmodel, create_section_state(), resource_manager)

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT_NAME)

        double_click_row(user, MARKER_SECTION_TABLE, SECTION_ROW)
        await wait_until_awaited(viewmodel.edit_selected_section_metadata)

        viewmodel.set_selected_section_ids.assert_called_with([SECTION_ID])
        viewmodel.edit_selected_section_metadata.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_double_click_does_nothing_while_disabled(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_viewmodel()
        target = SectionsForm(viewmodel, create_section_state(), resource_manager)

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT_NAME)
        target.disable()
        viewmodel.set_selected_section_ids.reset_mock()

        double_click_row(user, MARKER_SECTION_TABLE, SECTION_ROW)
        await wait_until_awaited(viewmodel.edit_selected_section_metadata)

        viewmodel.set_selected_section_ids.assert_not_called()
        viewmodel.edit_selected_section_metadata.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_double_click_works_again_after_enable(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        viewmodel = create_viewmodel()
        target = SectionsForm(viewmodel, create_section_state(), resource_manager)

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT_NAME)
        target.disable()
        target.enable()

        double_click_row(user, MARKER_SECTION_TABLE, SECTION_ROW)
        await wait_until_awaited(viewmodel.edit_selected_section_metadata)

        viewmodel.edit_selected_section_metadata.assert_awaited_once()
