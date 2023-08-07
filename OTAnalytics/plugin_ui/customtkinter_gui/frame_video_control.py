from typing import Any

from customtkinter import CTkButton, CTkFrame

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, STICKY


class FrameVideoControl(CTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.button_next_frame = CTkButton(
            master=self,
            text=">",
            command=self._viewmodel.next_frame,
        )
        self.button_previous_frame = CTkButton(
            master=self,
            text="<",
            command=self._viewmodel.previous_frame,
        )

    def _place_widgets(self) -> None:
        PADY = 10
        self.button_previous_frame.grid(
            row=0, column=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_next_frame.grid(
            row=0, column=2, padx=PADX, pady=PADY, sticky=STICKY
        )
