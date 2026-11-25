"""Tests that the canvas fills the space the time bar leaves."""

from unittest.mock import Mock

from nicegui import ui
from nicegui.testing import User

from OTAnalytics.plugin_ui.nicegui_gui.pages.workspace import (
    MARKER_WORKSPACE,
    Workspace,
)

ENDPOINT = "/test-workspace"
CANVAS = "canvas"


class TestWorkspace:
    async def test_canvas_fills_remaining_height(self, user: User) -> None:
        canvas = Mock()
        canvas.build.side_effect = lambda: ui.label(CANVAS)
        target = Workspace(Mock(), canvas)

        @ui.page(ENDPOINT)
        def page() -> None:
            target.build()

        await user.open(ENDPOINT)

        container = user.find(marker=MARKER_WORKSPACE).elements.pop()
        label = user.find(CANVAS).elements.pop()
        assert label.parent_slot is not None
        assert label.parent_slot.parent is container
        assert "ota-workspace" in container.classes
