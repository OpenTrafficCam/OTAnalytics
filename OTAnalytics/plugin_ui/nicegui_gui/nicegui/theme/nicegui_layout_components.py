from OTAnalytics.plugin_ui.nicegui_gui.nicegui.page_builder import LayoutComponents
from OTAnalytics.plugin_ui.nicegui_gui.pages.header.header_bar import HeaderBar


class NiceguiLayoutComponents(LayoutComponents):
    """Page-level layout parts, built before the page content as Quasar requires."""

    def __init__(self, header_bar: HeaderBar) -> None:
        self._header_bar = header_bar

    def build(self) -> None:
        self._header_bar.build()
