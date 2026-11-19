from nicegui import ui

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.page_builder import NiceguiPageBuilder
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.container import (
    ConfigurationBar,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.track_statistics_form.container import (
    TrackStatisticForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_filters import (
    VisualizationFilters,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers import (
    VisualizationLayers,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.workspace import Workspace

MARKER_LEFT_PANEL = "marker-left-panel"
MARKER_CENTER_PANEL = "marker-center-panel"
MARKER_RIGHT_PANEL = "marker-right-panel"
MARKER_STATUS_BAR = "marker-status-bar"


class MainPageBuilder(NiceguiPageBuilder):
    def __init__(
        self,
        endpoint_name: str,
        configuration_bar: ConfigurationBar,
        workspace: Workspace,
        visualization_filters: VisualizationFilters,
        visualization_layers: VisualizationLayers,
        status_bar: TrackStatisticForm,
    ) -> None:
        super().__init__(endpoint_name)
        self.configuration_bar = configuration_bar
        self.workspace = workspace
        self.visualization_filters = visualization_filters
        self.visualization_layers = visualization_layers
        self.status_bar = status_bar

    def _build(self) -> None:
        # The page keeps the window height, so only the side panels scroll.
        ui.query("body").classes("overflow-hidden")
        ui.query(".nicegui-content").classes("h-screen p-0 gap-0")
        with ui.row(wrap=False).classes("w-full flex-1 min-h-0 gap-0 no-wrap"):
            with (
                ui.column()
                .classes("w-[344px] shrink-0 h-full overflow-y-auto p-2")
                .mark(MARKER_LEFT_PANEL)
            ):
                self.configuration_bar.build()
            with (
                ui.column()
                .classes("flex-1 min-w-0 h-full flex flex-col p-2")
                .mark(MARKER_CENTER_PANEL)
            ):
                self.workspace.build()
                self.visualization_filters.build()
            with (
                ui.column()
                .classes("w-[288px] shrink-0 h-full overflow-y-auto p-2")
                .mark(MARKER_RIGHT_PANEL)
            ):
                self.visualization_layers.build()
        with (
            ui.row()
            .classes("w-full shrink-0 px-3 py-1 border-t bg-white")
            .mark(MARKER_STATUS_BAR)
        ):
            self.status_bar.build()
