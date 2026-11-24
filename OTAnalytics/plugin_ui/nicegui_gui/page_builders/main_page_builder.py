from nicegui import ui

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.page_builder import NiceguiPageBuilder
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.container import (
    ConfigurationBar,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.assignment_status import (  # noqa
    AssignmentStatus,
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
MARKER_PANEL_SPLITTER = "marker-panel-splitter"

LEFT_PANEL_WIDTH = 400
"""Initial width of the left panel in pixels."""
LEFT_PANEL_LIMITS = (280, 640)
"""Narrowest and widest the user can drag the left panel, in pixels."""


class MainPageBuilder(NiceguiPageBuilder):
    def __init__(
        self,
        endpoint_name: str,
        configuration_bar: ConfigurationBar,
        workspace: Workspace,
        visualization_filters: VisualizationFilters,
        visualization_layers: VisualizationLayers,
        status_bar: TrackStatisticForm,
        assignment_status: AssignmentStatus,
    ) -> None:
        super().__init__(endpoint_name)
        self.configuration_bar = configuration_bar
        self.workspace = workspace
        self.visualization_filters = visualization_filters
        self.visualization_layers = visualization_layers
        self.status_bar = status_bar
        self.assignment_status = assignment_status

    def _build(self) -> None:
        # The page keeps the window height, so only the side panels scroll.
        ui.query(".nicegui-content").classes("ota-app")
        # The user resizes the left panel by dragging the separator.
        with (
            ui.splitter(value=LEFT_PANEL_WIDTH, limits=LEFT_PANEL_LIMITS)
            .props("unit=px")
            .classes("ota-panels")
            .mark(MARKER_PANEL_SPLITTER) as splitter
        ):
            with splitter.before:
                with ui.column().classes("ota-left").mark(MARKER_LEFT_PANEL):
                    self.configuration_bar.build()
            with splitter.after:
                with ui.row(wrap=False).classes("ota-main"):
                    with ui.column().classes("ota-center").mark(MARKER_CENTER_PANEL):
                        self.workspace.build()
                        self.visualization_filters.build()
                    with ui.column().classes("ota-right").mark(MARKER_RIGHT_PANEL):
                        self.visualization_layers.build()
        with ui.row(wrap=False).classes("ota-statusbar").mark(MARKER_STATUS_BAR):
            self.status_bar.build()
            self.assignment_status.build()
