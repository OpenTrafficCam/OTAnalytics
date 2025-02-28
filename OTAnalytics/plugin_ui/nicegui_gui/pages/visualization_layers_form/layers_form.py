from datetime import datetime
from typing import Optional, Self, Sequence

from nicegui import ui

from OTAnalytics.adapter_ui.abstract_frame_track_plotting import (
    AbstractFrameTrackPlotting,
)
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.plotting import LayerGroup
from OTAnalytics.application.resources.resource_manager import ResourceManager

MARKER_PROJECT_NAME = "marker-project-name"
MARKER_START_DATE = "marker-start-date"
MARKER_START_TIME = "marker-start-time"


class LayersForm(AbstractFrameTrackPlotting):
    def __init__(
        self,
        view_model: ViewModel,
        resource_manager: ResourceManager,
        layers: Sequence[LayerGroup],
    ) -> None:
        self._view_model = view_model
        self._resource_manager = resource_manager
        self.introduce_to_viewmodel()
        self._layers = layers

    def introduce_to_viewmodel(self) -> None:
        pass

    def build(self) -> Self:
        for layer_group in self._layers:
            ui.label(layer_group.name)
            for layer in layer_group.layers:
                ui.checkbox(
                    layer.get_name(),
                    on_change=lambda event: layer.set_enabled(event.value),
                )
        return self

    def update(self, name: str, start_date: Optional[datetime]) -> None:
        pass

    def reset_layers(self) -> None:
        pass
