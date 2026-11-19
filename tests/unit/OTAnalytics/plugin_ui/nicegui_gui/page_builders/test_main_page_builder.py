"""Tests the three-panel frame of the main page."""

from unittest.mock import Mock

from nicegui import ui
from nicegui.element import Element
from nicegui.testing import User

from OTAnalytics.plugin_ui.nicegui_gui.page_builders.main_page_builder import (
    MARKER_CENTER_PANEL,
    MARKER_LEFT_PANEL,
    MARKER_RIGHT_PANEL,
    MARKER_STATUS_BAR,
    MainPageBuilder,
)

ENDPOINT = "/test-main-page"
CONFIGURATION = "configuration bar"
WORKSPACE = "workspace"
FILTERS = "visualization filters"
LAYERS = "visualization layers"
STATUS = "track statistics"
ASSIGNMENT = "assignment status"
PANEL_MARKERS = {
    MARKER_LEFT_PANEL,
    MARKER_CENTER_PANEL,
    MARKER_RIGHT_PANEL,
    MARKER_STATUS_BAR,
}


def part(text: str) -> Mock:
    part = Mock()
    part.build.side_effect = lambda: ui.label(text)
    return part


def ancestors(element: Element) -> list[Element]:
    result = []
    while (parent := element.parent_slot) is not None:
        element = parent.parent
        result.append(element)
    return result


def panel_of(user: User, text: str) -> Element:
    label = user.find(text).elements.pop()
    return next(
        element for element in ancestors(label) if PANEL_MARKERS & set(element._markers)
    )


class TestMainPageBuilder:
    async def test_builds_parts_in_their_panels(self, user: User) -> None:
        MainPageBuilder(
            ENDPOINT,
            configuration_bar=part(CONFIGURATION),
            workspace=part(WORKSPACE),
            visualization_filters=part(FILTERS),
            visualization_layers=part(LAYERS),
            status_bar=part(STATUS),
            assignment_status=part(ASSIGNMENT),
        ).build(Mock())

        await user.open(ENDPOINT)

        left = user.find(marker=MARKER_LEFT_PANEL).elements.pop()
        center = user.find(marker=MARKER_CENTER_PANEL).elements.pop()
        right = user.find(marker=MARKER_RIGHT_PANEL).elements.pop()
        assert panel_of(user, CONFIGURATION) is left
        assert panel_of(user, WORKSPACE) is center
        assert panel_of(user, FILTERS) is center
        assert panel_of(user, LAYERS) is right
        status_bar = user.find(marker=MARKER_STATUS_BAR).elements.pop()
        assert panel_of(user, STATUS) is status_bar
        assert panel_of(user, ASSIGNMENT) is status_bar

    async def test_only_side_panels_scroll(self, user: User) -> None:
        MainPageBuilder(
            ENDPOINT,
            configuration_bar=part(CONFIGURATION),
            workspace=part(WORKSPACE),
            visualization_filters=part(FILTERS),
            visualization_layers=part(LAYERS),
            status_bar=part(STATUS),
            assignment_status=part(ASSIGNMENT),
        ).build(Mock())

        await user.open(ENDPOINT)

        left = user.find(marker=MARKER_LEFT_PANEL).elements.pop()
        center = user.find(marker=MARKER_CENTER_PANEL).elements.pop()
        right = user.find(marker=MARKER_RIGHT_PANEL).elements.pop()
        assert "overflow-y-auto" in left.classes
        assert "overflow-y-auto" in right.classes
        assert "flex-1" in center.classes
        assert "min-w-0" in center.classes

    async def test_status_bar_keeps_one_line(self, user: User) -> None:
        """A wrapping status bar would shrink the canvas whenever a notice shows."""
        MainPageBuilder(
            ENDPOINT,
            configuration_bar=part(CONFIGURATION),
            workspace=part(WORKSPACE),
            visualization_filters=part(FILTERS),
            visualization_layers=part(LAYERS),
            status_bar=part(STATUS),
            assignment_status=part(ASSIGNMENT),
        ).build(Mock())

        await user.open(ENDPOINT)

        status_bar = user.find(marker=MARKER_STATUS_BAR).elements.pop()
        assert "no-wrap" in status_bar.classes
