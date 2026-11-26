from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    VisualizationLayersKeys,
    VisualizationOffsetSliderKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.visualization_offset_slider_form import (  # noqa
    VisualizationOffSetSliderForm,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
    LayersForm,
)


class VisualizationLayers:
    def __init__(
        self,
        resource_manager: ResourceManager,
        layers_form: LayersForm,
        offset_slider_form: VisualizationOffSetSliderForm,
    ) -> None:
        self._resource_manager = resource_manager
        self._layers_form = layers_form
        self._offset_slider_form = offset_slider_form

    def build(self) -> None:
        ui.label(
            self._resource_manager.get(
                VisualizationLayersKeys.LABEL_VISUALIZATION_LAYERS_FORM_HEADER
            )
        ).classes("ota-panel-title")

        self._layers_form.build()
        with ui.column().classes("ota-reference-point"):
            with ui.column().classes("gap-0"):
                ui.label(
                    self._resource_manager.get(
                        VisualizationOffsetSliderKeys.LABEL_TRACK_REFERENCE_POINT
                    )
                ).classes("ota-reference-title")
                ui.label(
                    self._resource_manager.get(
                        VisualizationOffsetSliderKeys.LABEL_DESCRIPTION
                    )
                ).classes("ota-reference-description")
            self._offset_slider_form.build()
