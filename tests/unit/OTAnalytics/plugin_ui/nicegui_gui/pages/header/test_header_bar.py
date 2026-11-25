"""Tests the app bar with the project title and actions."""

from unittest.mock import Mock

from nicegui import ui
from nicegui.element import Element
from nicegui.testing import User

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.theme.nicegui_layout_components import (  # noqa
    NiceguiLayoutComponents,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.header.header_bar import (
    MARKER_HEADER,
    HeaderBar,
)

ENDPOINT = "/test-header"
TITLE = "project title"
ACTIONS = "project actions"


def part(text: str) -> Mock:
    part = Mock()
    part.build.side_effect = lambda: ui.label(text)
    return part


def is_in(element: Element, ancestor: Element) -> bool:
    while (slot := element.parent_slot) is not None:
        element = slot.parent
        if element is ancestor:
            return True
    return False


class TestHeaderBar:
    async def test_shows_brand_title_and_actions_in_the_header(
        self, user: User, resource_manager: ResourceManager
    ) -> None:
        target = HeaderBar(resource_manager, part(TITLE), part(ACTIONS))

        @ui.page(ENDPOINT)
        def page() -> None:
            NiceguiLayoutComponents(target).build()

        await user.open(ENDPOINT)

        header = user.find(marker=MARKER_HEADER).elements.pop()
        assert isinstance(header, ui.header)
        assert "ota-header" in header.classes
        await user.should_see("OTAnalytics")
        for text in (TITLE, ACTIONS):
            assert is_in(user.find(text).elements.pop(), header), text
