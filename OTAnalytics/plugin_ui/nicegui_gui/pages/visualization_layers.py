from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    VisualizationLayersKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
    LayersForm,
)


class VisualizationLayers:
    def __init__(
        self,
        resource_manager: ResourceManager,
        layers_form: LayersForm,
    ) -> None:
        self._resource_manager = resource_manager
        self._layers_form = layers_form

    def build(self) -> None:
        ui.label(
            self._resource_manager.get(
                VisualizationLayersKeys.LABEL_VISUALIZATION_LAYERS_FORM_HEADER
            )
        )

        self._layers_form.build()
