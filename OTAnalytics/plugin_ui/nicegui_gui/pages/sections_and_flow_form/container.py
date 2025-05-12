from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    FlowAndSectionKeys,
    ResourceManager,
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
            section_tab = ui.tab(
                self._resource_manager.get(FlowAndSectionKeys.TAB_SECTION)
            )
            flow_tab = ui.tab(self._resource_manager.get(FlowAndSectionKeys.TAB_FLOW))
        with ui.tab_panels(tabs, value=section_tab).classes("w-full"):
            with ui.tab_panel(section_tab):
                self.sections_form.build()
            with ui.tab_panel(flow_tab):
                self.flow_form.build()
