import tkinter
from typing import Any, Optional

from customtkinter import CTkCheckBox, CTkFrame

from OTAnalytics.adapter_ui.abstract_frame_canvas import AbstractFrameCanvas
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, STICKY


class FrameTrackPlotting(AbstractFrameCanvas, CTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._show_tracks = tkinter.BooleanVar()
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.button_show_tracks = CTkCheckBox(
            master=self,
            text="Show tracks",
            command=self._update_show_tracks_state,
            variable=self._show_tracks,
            onvalue=True,
            offvalue=False,
        )

    def _place_widgets(self) -> None:
        PADY = 10
        self.button_show_tracks.grid(
            row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def update_show_tracks(self, value: Optional[bool]) -> None:
        new_value = value or False
        self._show_tracks.set(new_value)

    def _update_show_tracks_state(self) -> None:
        new_value = self._show_tracks.get()
        self._viewmodel.update_show_tracks_state(new_value)
