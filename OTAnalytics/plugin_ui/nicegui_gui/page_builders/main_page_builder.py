from nicegui import ui

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.page_builder import NiceguiPageBuilder
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_bar.container import TrackBar
from OTAnalytics.plugin_ui.nicegui_gui.pages.analysis_bar.container import AnalysisForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.container import (
    ConfigurationBar,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.container import (
    SectionsAndFlowForm,
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
        add_tracker_bar: TrackBar,
        sections_and_flow_bar: SectionsAndFlowForm,
        analysis_bar: AnalysisForm,
        workspace: Workspace,
        visualization_filters: VisualizationFilters,
        visualization_layers: VisualizationLayers,
    ) -> None:
        super().__init__(endpoint_name)
        self.configuration_bar = configuration_bar
        self.add_track_bar = add_tracker_bar
        self.sections_and_flow_bar = sections_and_flow_bar
        self.analysis_bar = analysis_bar
        self.workspace = workspace
        self.visualization_filters = visualization_filters
        self.visualization_layers = visualization_layers

    def _build(self) -> None:
        with ui.grid(columns=8).classes("w-full"):
            with ui.column().classes("col-span-1"):
                self.configuration_bar.build()
                self.add_track_bar.build()
                self.sections_and_flow_bar.build()
                self.analysis_bar.build()
            with ui.column().classes("col-span-6"):
                with ui.grid(rows=8):
                    with ui.row().classes("row-span-6"):
                        self.workspace.build()
                    with ui.row().classes("row-span-2"):
                        self.visualization_filters.build()
            with ui.column().classes("col-span-1"):
                self.visualization_layers.build()
