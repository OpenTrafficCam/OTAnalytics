from nicegui import ui

from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_frame import (
    ProjectFrame,
)


class ConfigurationBar:
    def __init__(self, project_frame: ProjectFrame) -> None:
        self.project_frame = project_frame

    def build(self) -> None:
        ui.label("Configuration Bar")
        self.project_frame.build()
