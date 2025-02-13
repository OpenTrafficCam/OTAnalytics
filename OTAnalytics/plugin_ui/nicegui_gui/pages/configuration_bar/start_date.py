from datetime import datetime
from typing import Optional

from nicegui import ui

from OTAnalytics.adapter_ui.abstract_frame_project import AbstractFrameProject
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import ResourceManager


class StartDateForm(AbstractFrameProject):
    def __init__(
        self,
        view_model: ViewModel,
        resource_manager: ResourceManager,
    ) -> None:
        self._view_model = view_model
        self._resource_manager = resource_manager
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._view_model.set_frame_project(self)

    def build(self) -> None:
        ui.label("Start Date")
        with ui.grid().classes("w-full"):
            with ui.row():
                ui.input(placeholder="").props("rounded outlined dense").style(
                    "max-width: 25%"
                )
                ui.input(placeholder="").props("rounded outlined dense").style(
                    "max-width: 10%"
                )
                ui.markdown(":")
                ui.input(placeholder="").props("rounded outlined dense").style(
                    "max-width: 10%"
                )
                ui.markdown(":")
                ui.input(placeholder="").props("rounded outlined dense").style(
                    "max-width: 10%"
                )

    def update(self, name: str, start_date: Optional[datetime]) -> None:
        pass

    def set_enabled_general_buttons(self, enabled: bool) -> None:
        raise NotImplementedError
