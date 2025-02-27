from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    ProjectKeys,
    ResourceManager,
    SvzMetadataKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.flow_form import (
    FlowForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.sections_form import (  # noqa
    SectionsForm,
)


class SectionsAndFlowForm:
    def __init__(
        self,
        resource_manager: ResourceManager,
        sections_form: SectionsForm,
        flow_form: FlowForm,
    ) -> None:
        self._resource_manager = resource_manager
        self.sections_form = sections_form
        self.flow_form = flow_form

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
                self.sections_form.build()
            with ui.tab_panel(two):
                self.flow_form.build()
