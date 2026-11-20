"""Tests the primary and secondary buttons of the design."""

from unittest.mock import Mock

from nicegui import ui
from nicegui.testing import User

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.ota_button import ota_button
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

ENDPOINT = "/test-ota-button"
MARKER = "marker-test-button"


def find_button(user: User) -> ui.button:
    button = user.find(marker=MARKER).elements.pop()
    assert isinstance(button, ui.button)
    return button


class TestOtaButton:
    async def test_primary_button_is_filled(self, user: User) -> None:
        @ui.page(ENDPOINT)
        def page() -> None:
            ota_button("Add", Mock(), MARKER, icon="add")

        await user.open(ENDPOINT)

        button = find_button(user)
        assert button.text == "Add"
        assert button.props["icon"] == "add"
        assert "outline" not in button.props
        assert TEST_ID not in button.props

    async def test_secondary_button_is_outlined(self, user: User) -> None:
        @ui.page(ENDPOINT)
        def page() -> None:
            ota_button("Remove", Mock(), MARKER, secondary=True)

        await user.open(ENDPOINT)

        assert find_button(user).props["outline"] is True

    async def test_sets_test_id_on_request(self, user: User) -> None:
        @ui.page(ENDPOINT)
        def page() -> None:
            ota_button("Remove", Mock(), MARKER, test_id=True)

        await user.open(ENDPOINT)

        assert find_button(user).props[TEST_ID] == MARKER

    async def test_click_calls_handler(self, user: User) -> None:
        on_click = Mock()

        @ui.page(ENDPOINT)
        def page() -> None:
            ota_button("Remove", on_click, MARKER)

        await user.open(ENDPOINT)
        user.find(marker=MARKER).click()

        on_click.assert_called_once()
