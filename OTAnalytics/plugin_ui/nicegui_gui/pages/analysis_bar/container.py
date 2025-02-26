from nicegui import ui

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    AnalysisKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)


class AnalysisForm:
    def __init__(
        self,
        resource_manager: ResourceManager,
        view_model: ViewModel,
    ) -> None:
        self._resource_manager = resource_manager
        self._viewmodel = view_model

    def build(self) -> None:
        ui.label(self._resource_manager.get(AnalysisKeys.LABEL_ANALYSIS))
        with ui.grid(rows=4):
            with ui.row():
                ui.button(
                    self._resource_manager.get(
                        AnalysisKeys.BUTTON_TEXT_EXPORT_EVENT_LIST
                    ),
                    on_click=self._viewmodel.export_events,
                )
            with ui.row():
                ui.button(
                    self._resource_manager.get(AnalysisKeys.BUTTON_TEXT_EXPORT_COUNTS),
                    on_click=self._viewmodel.export_counts,
                )
            with ui.row():
                ui.button(
                    self._resource_manager.get(
                        AnalysisKeys.BUTTON_TEXT_EXPORT_ROAD_USER_ASSIGNMENT
                    ),
                    on_click=self._viewmodel.export_road_user_assignments,
                )
            with ui.row():
                ui.button(
                    self._resource_manager.get(
                        AnalysisKeys.BUTTON_TEXT_EXPORT_TRACK_STATISTICS
                    ),
                    on_click=self._viewmodel.export_track_statistics,
                )
