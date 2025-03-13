from nicegui import ui

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.remarks_form.container import RemarkForm
from OTAnalytics.plugin_ui.nicegui_gui.pages.track_statistics_form.container import (
    TrackStatisticForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_filters_form.container import (  # noqa
    VisualizationFiltersForm,
)


class VisualizationFilters:
    def __init__(
        self,
        resource_manager: ResourceManager,
        visualization_filter: VisualizationFiltersForm,
        remarks: RemarkForm,
        track_statistic: TrackStatisticForm,
    ) -> None:
        self._resource_manager = resource_manager
        self._visualization_filter = visualization_filter
        self._remarks = remarks
        self._track_statistic = track_statistic

    def build(self) -> None:
        with ui.grid(rows=3):
            with ui.row():
                self._track_statistic.build()
            with ui.row():
                self._visualization_filter.build()
            with ui.row():
                self._remarks.build()
