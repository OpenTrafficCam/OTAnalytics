"""Tests for the custom table of the webui."""

from unittest.mock import AsyncMock, Mock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import CustomTable
from tests.utils.nicegui_table import (
    double_click_row,
    wait_until_awaited,
    wait_until_called,
)

ENDPOINT_NAME = "/test-custom-table"
MARKER_TABLE = "marker-test-table"
FIRST_ROW = {"id": "first", "name": "First"}
SECOND_ROW = {"id": "second", "name": "Second"}
COLUMNS = [{"name": "name", "label": "Name", "field": "name"}]


def create_target(
    on_row_double_click_method: AsyncMock | Mock | None = None,
) -> CustomTable:
    return CustomTable(
        columns=COLUMNS,
        rows=[dict(FIRST_ROW), dict(SECOND_ROW)],
        selection="multiple",
        marker=MARKER_TABLE,
        on_row_double_click_method=on_row_double_click_method,
    )


class TestCustomTableRowDoubleClick:

    @pytest.mark.asyncio
    async def test_double_click_passes_the_clicked_row_to_the_handler(
        self, user: User
    ) -> None:
        handler = AsyncMock()
        target = create_target(handler)

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT_NAME)

        double_click_row(user, MARKER_TABLE, SECOND_ROW)
        await wait_until_awaited(handler)

        handler.assert_awaited_once_with(SECOND_ROW)

    @pytest.mark.asyncio
    async def test_double_click_supports_synchronous_handlers(self, user: User) -> None:
        handler = Mock()
        target = create_target(handler)

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT_NAME)

        double_click_row(user, MARKER_TABLE, FIRST_ROW)
        await wait_until_called(handler)

        handler.assert_called_once_with(FIRST_ROW)

    @pytest.mark.asyncio
    async def test_double_click_without_handler_does_not_raise(
        self, user: User
    ) -> None:
        target = create_target()

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT_NAME)

        double_click_row(user, MARKER_TABLE, FIRST_ROW)
