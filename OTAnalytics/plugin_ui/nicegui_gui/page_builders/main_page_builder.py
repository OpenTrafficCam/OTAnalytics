from nicegui import ui

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.page_builder import NiceguiPageBuilder
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.container import (
    ConfigurationBar,
)
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
        with ui.grid(columns=8).classes("w-full"):
            with ui.column().classes("col-span-1"):
                self.configuration_bar.build()
            with ui.column().classes("col-span-6"):
                with ui.grid():
                    with ui.row():
                        self.workspace.build()
                    with ui.row():
                        self.visualization_filters.build()
            with ui.column().classes("col-span-1"):
                self.visualization_layers.build()
