from datetime import datetime
from typing import Callable, Optional, Self, Sequence

from nicegui import ui

from OTAnalytics.adapter_ui.abstract_frame_track_plotting import (
    AbstractFrameTrackPlotting,
)
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.plotting import Layer, LayerGroup
from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    VisualizationLayersKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.constants import TestIdAttributes
from OTAnalytics.plugin_ui.visualization.visualization import ALL

MARKER_PROJECT_NAME = "marker-project-name"
MARKER_START_DATE = "marker-start-date"
MARKER_START_TIME = "marker-start-time"
MARKER_VISUALIZATION_LAYERS_ALL = "marker-visualization-layers-all"
MARKER_UPDATE_FLOW_HIGHLIGHTING = "marker-update-flow-highlighting"


class LayersForm(AbstractFrameTrackPlotting):
    def __init__(
        self,
        viewmodel: ViewModel,
        resource_manager: ResourceManager,
        layers: Sequence[LayerGroup],
    ) -> None:
        self._viewmodel = viewmodel
        self._resource_manager = resource_manager
        self._layers = layers
        self._checkboxes: dict[Layer, ui.checkbox] = {}
        for layer_group in layers:
            for layer in layer_group.layers:
                layer.register(self._follow(layer))
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_track_plotting(self)

    def build(self) -> Self:
        self._checkboxes = {}
        for layer_group in self._layers:
            ui.label(layer_group.name)
            for layer in layer_group.layers:
                checkbox = ui.checkbox(
                    layer.get_name(),
                    value=layer.is_enabled(),
                    on_change=lambda event, current=layer: current.set_enabled(
                        event.value
                    ),
                )
                self._checkboxes[layer] = checkbox
                if layer_group.name == "Show tracks" and layer.get_name() == ALL:
                    checkbox.mark(MARKER_VISUALIZATION_LAYERS_ALL)
                    checkbox.props(
                        f"{TestIdAttributes.DATA_TESTID}={MARKER_VISUALIZATION_LAYERS_ALL}"  # noqa
                    )
        button = ui.button(
            self._resource_manager.get(
                VisualizationLayersKeys.BUTTON_UPDATE_FLOW_HIGHLIGHTING
            ),
            on_click=self._create_events,
        )
        button.mark(MARKER_UPDATE_FLOW_HIGHLIGHTING)
        button.props(
            f"{TestIdAttributes.DATA_TESTID}={MARKER_UPDATE_FLOW_HIGHLIGHTING}"
        )
        return self

    def _create_events(self) -> None:
        self._viewmodel.create_events()

    def update(self, name: str, start_date: Optional[datetime]) -> None:
        pass

    def _follow(self, layer: Layer) -> Callable[[bool], None]:
        return lambda enabled: self._show(layer, enabled)

    def _show(self, layer: Layer, enabled: bool) -> None:
        """Follow layer changes made elsewhere, e.g. by resetting the application.

        The layers outlive the page: the checkboxes are rebuilt on every visit, so
        only those of the latest build are updated.
        """
        if checkbox := self._checkboxes.get(layer):
            checkbox.set_value(enabled)
