from typing import Optional

from nicegui import ui
from nicegui.elements.button import Button

from OTAnalytics.adapter_ui.abstract_frame import AbstractFrame
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    AnalysisKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.button_form import ButtonForm


class AnalysisForm(ButtonForm, AbstractFrame):
    def __init__(
        self,
        resource_manager: ResourceManager,
        view_model: ViewModel,
    ) -> None:
        self._resource_manager = resource_manager
        self._viewmodel = view_model
        self._button_export_event_list: Optional[Button] = None
        self._button_export_counts: Optional[Button] = None
        self._button_export_road_user_assignment: Optional[Button] = None
        self._button_export_track_statistics: Optional[Button] = None
        self._introduce_to_viewmodel()

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_analysis_frame(self)

    def build(self) -> None:
        ui.label(self._resource_manager.get(AnalysisKeys.LABEL_ANALYSIS))
        with ui.grid(rows=4):
            with ui.row():
                self._button_export_event_list = ui.button(
                    self._resource_manager.get(
                        AnalysisKeys.BUTTON_TEXT_EXPORT_EVENT_LIST
                    ),
                    on_click=self._viewmodel.export_events,
                )
            with ui.row():
                self._button_export_counts = ui.button(
                    self._resource_manager.get(AnalysisKeys.BUTTON_TEXT_EXPORT_COUNTS),
                    on_click=self._viewmodel.export_counts,
                )
            with ui.row():
                self._button_export_road_user_assignment = ui.button(
                    self._resource_manager.get(
                        AnalysisKeys.BUTTON_TEXT_EXPORT_ROAD_USER_ASSIGNMENT
                    ),
                    on_click=self._viewmodel.export_road_user_assignments,
                )
            with ui.row():
                self._button_export_track_statistics = ui.button(
                    self._resource_manager.get(
                        AnalysisKeys.BUTTON_TEXT_EXPORT_TRACK_STATISTICS
                    ),
                    on_click=self._viewmodel.export_track_statistics,
                )

    def get_general_buttons(self) -> list[Button]:
        general_buttons = []
        if self._button_export_event_list:
            general_buttons.append(self._button_export_event_list)
        if self._button_export_counts:
            general_buttons.append(self._button_export_counts)
        if self._button_export_road_user_assignment:
            general_buttons.append(self._button_export_road_user_assignment)
        if self._button_export_track_statistics:
            general_buttons.append(self._button_export_track_statistics)
        return general_buttons
