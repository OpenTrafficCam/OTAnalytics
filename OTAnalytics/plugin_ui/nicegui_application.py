from functools import cached_property

from OTAnalytics.plugin_ui.gui_application import OtAnalyticsGuiApplicationStarter
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.container import (
    ConfigurationBar,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_frame import (
    ProjectFrame,
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
        from plugin_ui.nicegui_gui.nicegui.theme.nicegui_layout_components import (
            NiceguiLayoutComponents,
        )

        return NiceguiWebserver(
            page_builders=[main_page_builder],
            layout_components=NiceguiLayoutComponents(),
            hostname="localhost",
            port=5000,
        ).run()

    @cached_property
    def configuration_bar(self) -> ConfigurationBar:
        return ConfigurationBar(self.project_frame)

    @cached_property
    def project_frame(self) -> ProjectFrame:
        return ProjectFrame()

    @cached_property
    def workspace(self) -> Workspace:
        return Workspace()

    @cached_property
    def visualization_filters(self) -> VisualizationFilters:
        return VisualizationFilters()

    @cached_property
    def visualization_layers(self) -> VisualizationLayers:
        return VisualizationLayers()
