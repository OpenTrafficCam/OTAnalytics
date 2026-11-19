"""Tests editing a section by double-clicking it in the WebUI section table."""

from typing import Any
from unittest.mock import MagicMock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.application.state import SectionState
from OTAnalytics.domain.section import SectionType
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.sections_form import (  # noqa
    COLUMN_TYPE,
    MARKER_BUTTON_ADD_AREA,
    MARKER_BUTTON_ADD_LINE,
    MARKER_BUTTON_EDIT,
    MARKER_BUTTON_PROPERTIES,
    MARKER_BUTTON_REMOVE,
    MARKER_SECTION_TABLE,
    SectionsForm,
    create_columns,
    map_to_ui,
)
from tests.utils.nicegui_table import double_click_row, wait_until_awaited

ENDPOINT_NAME = "/test-sections-form-double-click"
SECTION_ID = "section-1"
SECTION_ROW = {"id": SECTION_ID, "name": "Section 1"}


class FakeSection:
    def __init__(
        self, section_id: str, name: str, section_type: SectionType = SectionType.LINE
    ) -> None:
        self.id = section_id
        self.name = name
        self.section_type = section_type

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "name": self.name}

    def get_type(self) -> SectionType:
        return self.section_type


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


class TestSectionType:
    def test_table_has_a_type_column(self, resource_manager: ResourceManager) -> None:
        names = [column["name"] for column in create_columns(resource_manager)]

        assert COLUMN_TYPE in names

    def test_rows_name_the_section_type(
        self, resource_manager: ResourceManager
    ) -> None:
        sections = [
            FakeSection("1", "West", SectionType.LINE),
            FakeSection("2", "Crossing", SectionType.AREA),
            FakeSection("3", "#clip", SectionType.CUTTING),
        ]

        rows = map_to_ui(sections, resource_manager)  # type: ignore[arg-type]

        assert [row[COLUMN_TYPE] for row in rows] == ["Line", "Area", "Cutting"]

    async def test_shows_the_type_as_a_tag(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = SectionsForm(
            create_viewmodel(), create_section_state(), resource_manager
        )

        @ui.page("/test-section-type")
        def page() -> None:
            target.build()

        await user.open("/test-section-type")

        table = user.find(marker=MARKER_SECTION_TABLE).elements.pop()
        assert f"body-cell-{COLUMN_TYPE}" in table.slots
        assert "ota-tag" in str(table.slots[f"body-cell-{COLUMN_TYPE}"].template)


class TestSectionButtons:
    async def test_add_line_is_the_primary_action_before_the_list(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = SectionsForm(
            create_viewmodel(), create_section_state(), resource_manager
        )

        @ui.page("/test-section-buttons")
        def page() -> None:
            target.build()

        await user.open("/test-section-buttons")

        def props(marker: str) -> dict:
            return user.find(marker=marker).elements.pop().props

        assert "outline" not in props(MARKER_BUTTON_ADD_LINE)
        for marker in (
            MARKER_BUTTON_ADD_AREA,
            MARKER_BUTTON_EDIT,
            MARKER_BUTTON_PROPERTIES,
            MARKER_BUTTON_REMOVE,
        ):
            assert "outline" in props(marker), marker
        assert user.client is not None
        order = [
            marker
            for element in user.client.layout.descendants()
            for marker in element._markers
            if marker in (MARKER_BUTTON_ADD_LINE, MARKER_SECTION_TABLE)
        ]
        assert order == [MARKER_BUTTON_ADD_LINE, MARKER_SECTION_TABLE]
