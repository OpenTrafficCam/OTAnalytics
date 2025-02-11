from nicegui import ui

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.page_builder import NiceguiPageBuilder
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar import ConfigurationBar
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_filters import (
    VisualizationFilters,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers import (
    VisualizationLayers,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.workspace import Workspace


class MainPageBuilder(NiceguiPageBuilder):
    def __init__(
        self,
        endpoint_name: str,
        configuration_bar: ConfigurationBar,
        workspace: Workspace,
        visualization_filters: VisualizationFilters,
        visualization_layers: VisualizationLayers,
    ) -> None:
        super().__init__(endpoint_name)
        self.configuration_bar = configuration_bar
        self.workspace = workspace
        self.visualization_filters = visualization_filters
        self.visualization_layers = visualization_layers

    def _build(self) -> None:
        with ui.grid(columns=3).classes("w-full"):
            with ui.column():
                self.configuration_bar.build()
            with ui.column():
                self.workspace.build()
                self.visualization_filters.build()
            with ui.column():
                self.visualization_layers.build()
