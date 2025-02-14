import uvicorn
from fastapi import FastAPI
from nicegui import ui

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.page_builder import (
    LayoutComponents,
    NiceguiPageBuilder,
)


class NiceguiWebserver:
    def __init__(
        self,
        page_builders: list[NiceguiPageBuilder],
        layout_components: LayoutComponents,
        hostname: str,
        port: int = 5000,
        hot_reload: bool = False,
    ) -> None:
        self._page_builders = page_builders
        self._layout_components = layout_components
        self._hostname = hostname
        self._port = port
        self._hot_reload = hot_reload

    def run(self) -> None:
        app = FastAPI()
        self.build_pages()
        ui.run_with(app)
        uvicorn.run(app, host=self._hostname, port=self._port)

    def build_pages(self) -> None:
        for page_builder in self._page_builders:
            page_builder.build(self._layout_components)
