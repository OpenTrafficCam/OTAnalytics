from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    WorkspaceKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.container import (
    CanvasAndFilesForm,
)


class Workspace:
    def __init__(
        self, resource_manager: ResourceManager, canvas_files_bar: CanvasAndFilesForm
    ) -> None:
        self._resource_manager = resource_manager
        self._canvas_files_bar = canvas_files_bar

    def build(self) -> None:
        ui.label(self._resource_manager.get(WorkspaceKeys.LABEL_WORKSPACE_FORM_HEADER))
        self._canvas_files_bar.build()
