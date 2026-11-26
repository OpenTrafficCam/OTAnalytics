from nicegui import ui

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_form import (
    ProjectActions,
    ProjectTitle,
)

MARKER_HEADER = "marker-header"
BRAND = "OTAnalytics"


class HeaderBar:
    """App bar with the brand, the project title and the project actions."""

    def __init__(
        self,
        resource_manager: ResourceManager,
        title: ProjectTitle,
        actions: ProjectActions,
    ) -> None:
        self._resource_manager = resource_manager
        self._title = title
        self._actions = actions

    def build(self) -> None:
        with ui.header(elevated=False).classes("ota-header").mark(MARKER_HEADER):
            with ui.row(wrap=False).classes("ota-brand"):
                ui.icon("videocam").classes("ota-brand-icon")
                ui.label(BRAND)
            ui.element("div").classes("ota-header-divider")
            self._title.build()
            with ui.row(wrap=False).classes("ota-header-actions"):
                self._actions.build()
