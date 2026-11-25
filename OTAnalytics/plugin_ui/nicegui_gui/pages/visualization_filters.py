from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_filters_form.container import \
    VisualizationFiltersForm  # noqa


class VisualizationFilters:
    def __init__(
        self,
        resource_manager: ResourceManager,
        visualization_filter: VisualizationFiltersForm,
    ) -> None:
        self._resource_manager = resource_manager
        self._visualization_filter = visualization_filter

    def build(self) -> None:
        self._visualization_filter.build()
