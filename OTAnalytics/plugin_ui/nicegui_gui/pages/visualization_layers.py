from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    VisualizationLayersKeys,
)


class VisualizationLayers:
    def __init__(
        self,
        resource_manager: ResourceManager,
    ) -> None:
        self._resource_manager = resource_manager

    def build(self) -> None:
        ui.label(
            self._resource_manager.get(
                VisualizationLayersKeys.LABEL_VISUALIZATION_LAYERS_FORM_HEADER
            )
        )
