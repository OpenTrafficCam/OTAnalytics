from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    ProjectKeys,
    ResourceManager,
    SvzMetadataKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.container import TrackForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.analysis_form.container import AnalysisForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_form import (
    ProjectForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.container import (
    SectionsAndFlowForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.svz_metadata_form.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)


class ConfigurationBar:
    def __init__(
        self,
        resource_manager: ResourceManager,
        project_form: ProjectForm,
        svz_metadata_form: SvzMetadataForm,
        track_form: TrackForm,
        sections_and_flow_form: SectionsAndFlowForm,
        analysis_form: AnalysisForm,
    ) -> None:
        self._resource_manager = resource_manager
        self.project_form = project_form
        self.svz_metadata_form = svz_metadata_form
        self.track_form = track_form
        self.sections_and_flow_form = sections_and_flow_form
        self.analysis_form = analysis_form

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
                self.project_form.build()
            with ui.tab_panel(two):
                self.svz_metadata_form.build()

        self.track_form.build()
        self.sections_and_flow_form.build()
        self.analysis_form.build()
