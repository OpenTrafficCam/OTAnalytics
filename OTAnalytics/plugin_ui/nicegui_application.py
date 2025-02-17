from functools import cached_property

from OTAnalytics.plugin_ui.gui_application import OtAnalyticsGuiApplicationStarter
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.container import (
    ConfigurationBar,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_form import (
    ProjectForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_filters import (
    VisualizationFilters,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers import (
    VisualizationLayers,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.workspace import Workspace


class OtAnalyticsNiceGuiApplicationStarter(OtAnalyticsGuiApplicationStarter):

    def start_ui(self) -> None:
        from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
        from OTAnalytics.plugin_ui.nicegui_gui.nicegui.nicegui_webserver import (
            NiceguiWebserver,
        )
        from OTAnalytics.plugin_ui.nicegui_gui.nicegui.theme.nicegui_layout_components import (  # noqa
            NiceguiLayoutComponents,
        )
        from OTAnalytics.plugin_ui.nicegui_gui.page_builders.main_page_builder import (
            MainPageBuilder,
        )

        main_page_builder = MainPageBuilder(
            ENDPOINT_MAIN_PAGE,
            configuration_bar=self.configuration_bar,
            workspace=self.workspace,
            visualization_filters=self.visualization_filters,
            visualization_layers=self.visualization_layers,
        )

        return NiceguiWebserver(
            page_builders=[main_page_builder],
            layout_components=NiceguiLayoutComponents(),
            hostname="localhost",
            port=5000,
        ).run()

    @cached_property
    def configuration_bar(self) -> ConfigurationBar:
        return ConfigurationBar(
            self.resource_manager, self.project_form, self.svz_metadata_form
        )

    @cached_property
    def project_form(self) -> ProjectForm:
        return ProjectForm(self.view_model, self.resource_manager)

    @cached_property
    def svz_metadata_form(self) -> SvzMetadataForm:
        return SvzMetadataForm(self.view_model, self.resource_manager)

    @cached_property
    def workspace(self) -> Workspace:
        return Workspace(self.resource_manager)

    @cached_property
    def visualization_filters(self) -> VisualizationFilters:
        return VisualizationFilters(self.resource_manager)

    @cached_property
    def visualization_layers(self) -> VisualizationLayers:
        return VisualizationLayers(self.resource_manager)
