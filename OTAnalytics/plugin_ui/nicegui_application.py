from OTAnalytics.plugin_ui.gui_application import OtAnalyticsGuiApplicationStarter


class OtAnalyticsNiceGuiApplicationStarter(OtAnalyticsGuiApplicationStarter):

    def start_ui(self) -> None:
        from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
        from OTAnalytics.plugin_ui.nicegui_gui.nicegui.nicegui_webserver import (
            NiceguiWebserver,
        )
        from OTAnalytics.plugin_ui.nicegui_gui.page_builders.main_page_builder import (
            MainPageBuilder,
        )

        main_page_builder = MainPageBuilder(ENDPOINT_MAIN_PAGE)
        from plugin_ui.nicegui_gui.nicegui.theme.nicegui_layout_components import (
            NiceguiLayoutComponents,
        )

        return NiceguiWebserver(
            page_builders=[main_page_builder],
            layout_components=NiceguiLayoutComponents(),
            hostname="localhost",
            port=5000,
        ).run()
