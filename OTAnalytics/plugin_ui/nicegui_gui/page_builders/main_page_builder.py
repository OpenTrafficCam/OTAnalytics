from nicegui import ui

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.page_builder import NiceguiPageBuilder


class MainPageBuilder(NiceguiPageBuilder):
    def __init__(self, endpoint_name: str) -> None:
        super().__init__(endpoint_name)

    def _build(self) -> None:
        ui.label("Hallo")
