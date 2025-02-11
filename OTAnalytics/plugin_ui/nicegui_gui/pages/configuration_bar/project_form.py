from datetime import datetime
from typing import Any, Callable, Optional, Self

from nicegui import ui
from nicegui.events import ClickEventArguments, ValueChangeEventArguments

from OTAnalytics.adapter_ui.abstract_button_quick_save_config import (
    AbstractButtonQuickSaveConfig,
)
from OTAnalytics.adapter_ui.abstract_frame_project import AbstractFrameProject
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.style import COLOR_ORANGE
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import FormFieldText

LABEL_PROJECT_NAME = "Project name"
MARKER_PROJECT_NAME = "marker-project-name"


class NiceGuiButtonQuickSaveConfig(AbstractButtonQuickSaveConfig):

    def __init__(
        self, text: str, on_click: Optional[Callable[[ClickEventArguments], Any]] = None
    ):
        self._text = text
        self._on_click = on_click

    def build(self) -> None:
        self._instance = ui.button(self._text, on_click=self._on_click)

    def set_state_changed_color(self) -> None:
        if self._instance:
            self._instance.style.update({"color": COLOR_ORANGE})

    def set_default_color(self) -> None:
        pass


class ProjectForm(AbstractFrameProject):
    def __init__(self, view_model: ViewModel) -> None:
        self._view_model = view_model
        self._quick_save_button = NiceGuiButtonQuickSaveConfig(
            "Save", on_click=self._quick_save
        )
        self._files = FormFieldText(
            LABEL_PROJECT_NAME,
            "",
            marker=MARKER_PROJECT_NAME,
            on_value_change=self._update_to_model,
        )
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._view_model.set_frame_project(self)
        self._view_model.set_button_quick_save_config(self._quick_save_button)

    def build(self) -> Self:
        ui.label("Project").classes("text-lg font-bold")
        with ui.row():
            ui.button("Open...")
            ui.button("Save as...")
            self._quick_save_button.build()
        self._files.build()
        return self

    def _update_to_model(self, events: ValueChangeEventArguments) -> None:
        self._view_model.update_project_name(events.value)

    def _quick_save(self, _: ClickEventArguments) -> None:
        self._view_model.quick_save_configuration()

    def update(self, name: str, start_date: Optional[datetime]) -> None:
        pass

    def set_enabled_general_buttons(self, enabled: bool) -> None:
        pass
