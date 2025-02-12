from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    ConfigurationBarKeys,
    ProjectKeys,
    ResourceManager,
    SvzMetadataKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_form import (
    ProjectForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)


class ConfigurationBar:
    def __init__(
        self,
        resource_manager: ResourceManager,
        project_form: ProjectForm,
        svz_metadata_form: SvzMetadataForm,
    ) -> None:
        self._resource_manager = resource_manager
        self.project_form = project_form
        self.svz_metadata_form = svz_metadata_form

    def build(self) -> None:
        ui.label(
            self._resource_manager.get(
                ConfigurationBarKeys.LABEL_CONFIGURATION_BAR_FORM_HEADER
            )
        )
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
                self.project_form.build()
            with ui.tab_panel(two):
                self.svz_metadata_form.build()
