from nicegui import ui

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.page_builder import (
    LayoutComponents,
    NiceguiPageBuilder,
)


class NiceguiDesktop:
    def __init__(
        self,
        page_builders: list[NiceguiPageBuilder],
        layout_components: LayoutComponents,
    ) -> None:
        self._page_builders = page_builders
        self._layout_components = layout_components

    def run(self) -> None:
        self.build_pages()
        ui.run(native=True)

    def build_pages(self) -> None:
        for page_builder in self._page_builders:
            page_builder.build(self._layout_components)
