from abc import ABC, abstractmethod

from fastapi import FastAPI, Request


class FastApiEndpointBuilder(ABC):
    def __init__(self, endpoint_name: str):
        self._endpoint_name = endpoint_name

    @abstractmethod
    def build(self, app: FastAPI) -> None:
        raise NotImplementedError


class NoParameterFastApiEndpointBuilder(FastApiEndpointBuilder):

    def build(self, app: FastAPI) -> None:
        @app.post(self._endpoint_name)
        async def build(request: Request) -> None:
            await self._handle_request(request)

    @abstractmethod
    async def _handle_request(self, request: Request) -> None:
        raise NotImplementedError
