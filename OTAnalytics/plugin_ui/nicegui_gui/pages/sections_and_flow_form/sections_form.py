from typing import Self

from nicegui import ui

from OTAnalytics.adapter_ui.abstract_frame_project import AbstractFrameSvzMetadata
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import ResourceManager


class SectionsForm(AbstractFrameSvzMetadata):
    def __init__(
        self,
        view_model: ViewModel,
        resource_manager: ResourceManager,
    ) -> None:
        self._view_model = view_model
        self._resource_manager = resource_manager

        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._view_model.set_svz_metadata_frame(self)

    def build(self) -> Self:
        # ui.table()
        with ui.grid(rows=3):
            with ui.row():
                ui.button()
                ui.button()
            with ui.row():
                ui.button()
                ui.button()
            with ui.row():
                ui.button()
        return self

    def update(self, metadata: dict) -> None:
        pass
