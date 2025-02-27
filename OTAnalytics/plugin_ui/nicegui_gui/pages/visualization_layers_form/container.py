from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.svz_metadata_form import (  # noqa
    SvzMetadataForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
    LayersForm,
)


class VisualizationLayerForm:
    def __init__(
        self,
        resource_manager: ResourceManager,
        layers_form: LayersForm,
    ) -> None:
        self._resource_manager = resource_manager
        self._layers_form = layers_form

    def build(self) -> None:
        self._layers_form.build()
