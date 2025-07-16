from datetime import datetime
from typing import Any, Callable, Optional, Self

from nicegui import ui
from nicegui.elements.button import Button
from nicegui.events import ClickEventArguments, ValueChangeEventArguments

from OTAnalytics.adapter_ui.abstract_button_quick_save_config import (
    AbstractButtonQuickSaveConfig,
)
from OTAnalytics.adapter_ui.abstract_frame_project import AbstractFrameProject
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    ProjectKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.customtkinter_gui.style import COLOR_ORANGE
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import (
    DateTimeForm,
    FormFieldText,
)

MARKER_PROJECT_NAME = "marker-project-name"
MARKER_START_DATE = "marker-start-date"
MARKER_START_TIME = "marker-start-time"


class NiceGuiButtonQuickSaveConfig(AbstractButtonQuickSaveConfig):

    def __init__(
        self, text: str, on_click: Optional[Callable[[ClickEventArguments], Any]] = None
    ):
        self._text = text
        self._on_click = on_click
        self._instance: ui.button | None = None

    def build(self) -> None:
        self._instance = ui.button(self._text, on_click=self._on_click)

    def set_state_changed_color(self) -> None:
        if self._instance:
            self._instance.style.update({"color": COLOR_ORANGE})

    def set_default_color(self) -> None:
        pass

    def enable(self) -> None:
        if self._instance:
            self._instance.enable()

    def disable(self) -> None:
        if self._instance:
            self._instance.disable()


class ProjectForm(ButtonForm, AbstractFrameProject):
    def __init__(
        self,
        view_model: ViewModel,
        resource_manager: ResourceManager,
    ) -> None:
        self._view_model = view_model
        self._resource_manager = resource_manager
        self.save_project_button: ui.button | None = None
        self.open_project_button: ui.button | None = None
        self._quick_save_button = NiceGuiButtonQuickSaveConfig(
            self._resource_manager.get(ProjectKeys.LABEL_QUICK_SAVE),
            on_click=self._quick_save,
        )
        self._project_name = FormFieldText(
            self._resource_manager.get(ProjectKeys.LABEL_PROJECT_NAME),
            "",
            marker=MARKER_PROJECT_NAME,
            on_value_change=self._update_to_model,
        )
        self._start_date = DateTimeForm(
            self._resource_manager.get(ProjectKeys.LABEL_START_DATE),
            self._resource_manager.get(ProjectKeys.LABEL_START_TIME),
            on_value_change=self._update_start_date_to_model,
            marker_date=MARKER_START_DATE,
            marker_time=MARKER_START_TIME,
        )
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._view_model.set_frame_project(self)
        self._view_model.set_button_quick_save_config(self._quick_save_button)

    def build(self) -> Self:
        ui.label(
            self._resource_manager.get(ProjectKeys.LABEL_PROJECT_FORM_HEADER)
        ).classes("text-lg font-bold")
        with ui.row():
            self.open_project_button = ui.button(
                self._resource_manager.get(ProjectKeys.LABEL_OPEN_PROJECT),
                on_click=self._open_project,
            )
            self.save_project_button = ui.button(
                self._resource_manager.get(ProjectKeys.LABEL_SAVE_AS_PROJECT),
                on_click=self._save_project,
            )
            self._quick_save_button.build()
        self._project_name.build()
        self._start_date.build()
        return self

    def _update_to_model(self, events: ValueChangeEventArguments) -> None:
        self._view_model.update_project_name(events.value)

    def _update_start_date_to_model(self, value: datetime | None) -> None:
        self._view_model.update_project_start_date(value)

    async def _quick_save(self, _: ClickEventArguments) -> None:
        await self._view_model.quick_save_configuration()

    async def _save_project(self, _: ClickEventArguments) -> None:
        await self._view_model.save_configuration()

    async def _open_project(self, _: ClickEventArguments) -> None:
        await self._view_model.load_configuration()

    def update(self, name: str, start_date: Optional[datetime]) -> None:
        if self._project_name._instance:
            self._project_name.set_value(name)
        if (
            start_date
            and hasattr(self._start_date, "_start_date")
            and self._start_date._start_date._instance
        ):
            self._start_date.set_value(start_date)

    def get_general_buttons(self) -> list[Button]:
        buttons = []
        if self._quick_save_button._instance:
            buttons.append(self._quick_save_button._instance)
        if self.open_project_button:
            buttons.append(self.open_project_button)
        if self.save_project_button:
            buttons.append(self.save_project_button)
        return buttons
