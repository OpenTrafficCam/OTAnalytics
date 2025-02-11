from nicegui import ui

from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_form import (
    ProjectForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)


class ConfigurationBar:
    def __init__(
        self, project_form: ProjectForm, svz_metadata_form: SvzMetadataForm
    ) -> None:
        self.project_form = project_form
        self.svz_metadata_form = svz_metadata_form

    def build(self) -> None:
        ui.label("Configuration Bar")
        with ui.tabs().classes("w-full") as tabs:
            one = ui.tab("Project")
            two = ui.tab("SVZ")
        with ui.tab_panels(tabs, value=one).classes("w-full"):
            with ui.tab_panel(one):
                self.project_form.build()
            with ui.tab_panel(two):
                self.svz_metadata_form.build()
