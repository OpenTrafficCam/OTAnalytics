from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (
    CanvasForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.files_form import (
    FilesForm,
)


class CanvasAndFilesForm:
    def __init__(
        self,
        resource_manager: ResourceManager,
        canvas_form: CanvasForm,
        files_form: FilesForm,
    ) -> None:
        self._resource_manager = resource_manager
        self.canvas_form = canvas_form
        self.files_form = files_form

    def build(self) -> None:
        self.canvas_form.build()
