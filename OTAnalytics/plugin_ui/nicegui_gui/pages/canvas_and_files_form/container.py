from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    ProjectKeys,
    ResourceManager,
    SvzMetadataKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (
    CanvasForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.files_form import (
    FilesForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.svz_metadata_form import (  # noqa
    SvzMetadataForm,
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
        with ui.tabs().classes("w-full") as tabs:
            one = ui.tab(
                self._resource_manager.get(ProjectKeys.LABEL_PROJECT_FORM_HEADER)
            )
            two = ui.tab(
                self._resource_manager.get(
                    SvzMetadataKeys.LABEL_SVZ_METADATA_FORM_HEADER
                )
            )
        with ui.tab_panels(tabs, value=one).classes("w-full"):
            with ui.tab_panel(one):
                self.canvas_form.build()
            with ui.tab_panel(two):
                self.files_form.build()
