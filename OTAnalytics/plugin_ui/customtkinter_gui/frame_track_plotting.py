import tkinter
from typing import Any, Sequence

from customtkinter import CTkButton, CTkCheckBox, CTkLabel

from OTAnalytics.adapter_ui.abstract_frame_track_plotting import (
    AbstractFrameTrackPlotting,
)
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.logger import logger
from OTAnalytics.application.plotting import Layer, LayerGroup
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.custom_containers import (
    CustomCTkTabview,
    EmbeddedCTkFrame,
)
from OTAnalytics.plugin_ui.customtkinter_gui.style import STICKY_WEST


class FrameTrackPlotting(AbstractFrameTrackPlotting, EmbeddedCTkFrame):
    def __init__(
        self, viewmodel: ViewModel, layers: Sequence[LayerGroup], **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._views: list[TabviewLayerGroup] = []
        self._layers = layers
        self._get_widgets()
        self._place_widgets()
        self.introduce_to_viewmodel()

    def _get_widgets(self) -> None:
        self._button_update_highlight_flows = CTkButton(
            master=self,
            text="Update Flow Highlighting",
            command=self._create_events,
        )

    def _place_widgets(self) -> None:
        self.grid_rowconfigure([i for i in range(0, len(self._layers))], weight=0)
        self.grid_rowconfigure(len(self._layers) + 1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        pady = 10
        for row, group in enumerate(self._layers):
            actual = TabviewLayerGroup(
                master=self,
                title=group.name,
                viewmodel=self._viewmodel,
                layers=group.layers,
            )
            actual.grid(
                row=row, column=0, padx=PADX, pady=(0, PADY), sticky=STICKY_WEST
            )
            self._views.append(actual)
        self._button_update_highlight_flows.grid(
            row=len(self._layers),
            column=0,
            padx=PADX,
            pady=(0, pady),
            sticky=STICKY,
        )

    def _create_events(self) -> None:
        logger().info("Creating events")
        self._viewmodel.create_events()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_track_plotting(self)

    def reset_layers(self) -> None:
        for view in self._views:
            view.reset_layers()


class TabviewLayerGroup(CustomCTkTabview):
    def __init__(
        self,
        viewmodel: ViewModel,
        title: str,
        layers: Sequence[Layer],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._get_widgets(viewmodel=viewmodel, layers=layers)
        self._place_widgets()
        self.disable_segmented_button()

    def _get_widgets(self, viewmodel: ViewModel, layers: Sequence[Layer]) -> None:
        self.add(self._title)
        self._frame = FrameTrackPlottingLayerGroup(
            master=self.tab(self._title), viewmodel=viewmodel, layers=layers
        )

    def _place_widgets(self) -> None:
        self._frame.pack(fill=tkinter.BOTH, expand=True)
        self.set(self._title)

    def reset_layers(self) -> None:
        self._frame.reset_layers()


class FrameTrackPlottingLayerGroup(EmbeddedCTkFrame):

    def __init__(
        self, viewmodel: ViewModel, layers: Sequence[Layer], **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self._view_model = viewmodel
        self._layers = layers
        self._place_widgets()

    def _place_widgets(self) -> None:
        self.grid_rowconfigure([i for i in range(0, len(self._layers))], weight=0)
        self.grid_rowconfigure(len(self._layers), weight=1)
        for row, layer in enumerate(self._layers):
            checkbox_layer = CheckBoxLayer(master=self, layer=layer)
            checkbox_layer.grid(
                row=row, column=0, padx=PADX, pady=(0, PADY), sticky=STICKY
            )

    def reset_layers(self) -> None:
        for layer in self._layers:
            layer.reset()


class CheckBoxLayer(EmbeddedCTkFrame):
    def __init__(self, layer: Layer, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._enabled = tkinter.BooleanVar()
        self._layer = layer
        self._enabled.set(self._layer.is_enabled())
        layer.register(self._on_layer_state_changed)
        self._get_widgets()

    def _get_widgets(self) -> None:
        self._label = CTkLabel(master=self, text=self._layer.get_name())
        self._checkbox = CTkCheckBox(
            master=self,
            text="",
            command=self._on_checkbox_clicked,
            variable=self._enabled,
            onvalue=True,
            offvalue=False,
            width=5,
        )
        self._checkbox.grid(row=0, column=0, padx=0, pady=0, sticky=STICKY_WEST)
        self._label.grid(row=0, column=1, padx=0, pady=0, sticky=STICKY_WEST)

    def _on_checkbox_clicked(self) -> None:
        self._layer.set_enabled(self._enabled.get())

    def _on_layer_state_changed(self, enabled: bool) -> None:
        self._enabled.set(enabled)
