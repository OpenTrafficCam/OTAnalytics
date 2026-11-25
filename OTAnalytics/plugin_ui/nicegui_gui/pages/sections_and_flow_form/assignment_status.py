from typing import Callable

from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    FlowKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

MARKER_ASSIGNMENT_OUTDATED = "marker-assignment-outdated"


class AssignmentStatus:
    """Status bar notice shown while the track assignment is out of date."""

    def __init__(
        self, resource_manager: ResourceManager, update_assignment: Callable[[], None]
    ) -> None:
        self._resource_manager = resource_manager
        self._update_assignment = update_assignment
        self._outdated = False
        # Created by `build()`, which runs when a browser asks for the page.
        self._notice: ui.row | None = None

    def build(self) -> None:
        with ui.row(wrap=False).classes("ota-assignment-notice") as self._notice:
            ui.icon("warning")
            ui.label(self._resource_manager.get(FlowKeys.LABEL_ASSIGNMENT_OUTDATED))
            ui.button(
                self._resource_manager.get(FlowKeys.BUTTON_UPDATE_OUTDATED),
                on_click=self._update_assignment,
            ).props("flat dense no-caps")
        self._notice.mark(MARKER_ASSIGNMENT_OUTDATED)
        self._notice.props(f"{TEST_ID}={MARKER_ASSIGNMENT_OUTDATED}")
        self._notice.set_visibility(self._outdated)

    def show_outdated(self, outdated: bool) -> None:
        self._outdated = outdated
        if self._notice is not None:
            self._notice.set_visibility(outdated)
