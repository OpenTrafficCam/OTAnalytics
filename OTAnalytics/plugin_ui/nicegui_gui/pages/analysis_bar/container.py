from nicegui import ui

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)


class AnalysisBar:
    def __init__(
        self,
        resource_manager: ResourceManager,
    ) -> None:
        self._resource_manager = resource_manager

    def build(self) -> None:
        with ui.grid(rows=4):
            with ui.row():
                ui.button()
            with ui.row():
                ui.button()
            with ui.row():
                ui.button()
            with ui.row():
                ui.button()
