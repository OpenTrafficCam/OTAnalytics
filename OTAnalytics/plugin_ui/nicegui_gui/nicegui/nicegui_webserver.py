import signal
from types import FrameType

import uvicorn
from fastapi import FastAPI
from nicegui import Client, core, nicegui, ui

from OTAnalytics.application.logger import logger
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.endpoint_builder import (
    FastApiEndpointBuilder,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.page_builder import (
    LayoutComponents,
    NiceguiPageBuilder,
)


class NiceguiWebserver:

    def __init__(
        self,
        endpoint_builders: list[FastApiEndpointBuilder],
        page_builders: list[NiceguiPageBuilder],
        layout_components: LayoutComponents,
        hostname: str,
        port: int = 5000,
        hot_reload: bool = False,
    ) -> None:
        self._endpoint_builders = endpoint_builders
        self._page_builders = page_builders
        self._layout_components = layout_components
        self._hostname = hostname
        self._port = port
        self._hot_reload = hot_reload

    def run(self) -> None:
        nicegui.app.on_shutdown(self.cleanup)
        # We also need to disconnect clients when the app is stopped with Ctrl+C,
        # because otherwise they will keep requesting images which lead to unfinished
        # subprocesses blocking the shutdown.
        signal.signal(signal.SIGINT, self.handle_sigint)

        fast_api_app = FastAPI()
        self.build_pages()
        self.build_endpoints(fast_api_app)
        ui.run_with(fast_api_app)

        logger().info(
            f"Running {self.__class__.__name__} on {self._hostname}:{self._port}"
        )
        uvicorn.run(
            fast_api_app,
            host=self._hostname,
            port=self._port,
            reload=False,
            log_level="warning",
        )

    async def disconnect(self) -> None:
        """Disconnect all clients from current running server."""
        for client_id in Client.instances:
            await core.sio.disconnect(client_id)

    def handle_sigint(self, signum: int, frame: FrameType | None) -> None:
        # Just call the default signal handler directly
        # This will trigger the normal shutdown process, including the registered
        # shutdown handler (self.cleanup)
        signal.default_int_handler(signum, frame)

    async def cleanup(self) -> None:
        # This prevents ugly stack traces when auto-reloading on code change,
        # because otherwise disconnected clients try to reconnect to the newly
        # started server.
        await self.disconnect()

    def build_pages(self) -> None:
        for page_builder in self._page_builders:
            page_builder.build(self._layout_components)

    def build_endpoints(self, app: FastAPI) -> None:
        for endpoint_builder in self._endpoint_builders:
            endpoint_builder.build(app)
