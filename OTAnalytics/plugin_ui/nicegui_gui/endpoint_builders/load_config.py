from application.use_cases.handle_load_otconfig import HandleLoadOtConfig
from fastapi import FastAPI
from starlette.requests import Request

from OTAnalytics.application.logger import logger
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.endpoint_builder import (
    FastApiEndpointBuilder,
)


class LoadConfigEndpointBuilder(FastApiEndpointBuilder):
    def __init__(
        self, endpoint_name: str, handle_load_otconfig: HandleLoadOtConfig
    ) -> None:
        super().__init__(endpoint_name)
        self.handle_load_otconfig = handle_load_otconfig

    def build(self, app: FastAPI) -> None:
        @app.post(self._endpoint_name)
        async def load_config(request: Request) -> None:
            payload = await request.json()
            logger().debug("Loading config: %s" % payload)
            self.handle_load_otconfig.load(payload)
