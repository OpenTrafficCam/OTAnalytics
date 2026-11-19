from nicegui import ui

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.container import (
    CanvasAndFilesForm,
)

MARKER_WORKSPACE = "marker-workspace"


class Workspace:
    def __init__(
        self, resource_manager: ResourceManager, canvas_files_bar: CanvasAndFilesForm
    ) -> None:
        self._resource_manager = resource_manager
        self._canvas_files_bar = canvas_files_bar

    def build(self) -> None:
        # Takes the height the time bar leaves and offers its size to the canvas.
        with (
            ui.element("div")
            .classes("relative flex-1 min-h-0 w-full flex items-center justify-center")
            .style("container-type: size")
            .mark(MARKER_WORKSPACE)
        ):
            self._canvas_files_bar.build()
