"""Tests the primary and secondary buttons of the design."""

from unittest.mock import Mock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button import CustomButton
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import (
    MissingInstanceError,
)
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

ENDPOINT = "/test-custom-button"
MARKER = "marker-test-button"


async def open_page(user: User, target: CustomButton) -> None:
    @ui.page(ENDPOINT)
    def page() -> None:
        target.build()

    await user.open(ENDPOINT)


class TestCustomButton:
    async def test_primary_button_is_filled(self, user: User) -> None:
        target = CustomButton("Add", Mock(), marker=MARKER, icon="add")

        await open_page(user, target)

        assert target.element.text == "Add"
        assert target.element.props["icon"] == "add"
        assert "outline" not in target.element.props

    async def test_secondary_button_is_outlined(self, user: User) -> None:
        target = CustomButton("Remove", Mock(), marker=MARKER, secondary=True)

        await open_page(user, target)

        assert target.element.props["outline"] is True

    async def test_marker_is_exposed_to_browser_tests(self, user: User) -> None:
        target = CustomButton("Remove", Mock(), marker=MARKER)

        await open_page(user, target)

        assert user.find(marker=MARKER).elements == {target.element}
        assert target.element.props[TEST_ID] == MARKER

    async def test_without_marker(self, user: User) -> None:
        target = CustomButton("Remove", Mock())

        await open_page(user, target)

        assert TEST_ID not in target.element.props

    async def test_click_calls_handler(self, user: User) -> None:
        on_click = Mock()

        await open_page(user, CustomButton("Remove", on_click, marker=MARKER))
        user.find(marker=MARKER).click()

        on_click.assert_called_once()

    def test_element_is_missing_before_build(self) -> None:
        with pytest.raises(MissingInstanceError):
            _ = CustomButton("Remove", Mock()).element
