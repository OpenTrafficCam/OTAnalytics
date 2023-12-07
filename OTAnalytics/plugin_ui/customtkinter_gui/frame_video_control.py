import tkinter
from typing import Any

from customtkinter import CTkButton, CTkEntry, CTkFrame, CTkLabel

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, STICKY


class FrameVideoControl(CTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._seconds = tkinter.IntVar(value=viewmodel.get_skip_seconds())
        self._frames = tkinter.IntVar(value=viewmodel.get_skip_frames())
        self._get_widgets()
        self._place_widgets()
        self._wire_widgets()

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
        self._label_seconds = CTkLabel(
            master=self, text="Seconds", anchor="e", justify="right"
        )
        self._label_frames = CTkLabel(
            master=self, text="Frames", anchor="e", justify="right"
        )
        self._entry_seconds = CTkEntry(master=self, textvariable=self._seconds)
        self._entry_frames = CTkEntry(master=self, textvariable=self._frames)

    def _place_widgets(self) -> None:
        PADY = 10
        self.button_previous_frame.grid(
            row=0, column=1, rowspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_seconds.grid(row=0, column=2, padx=PADX, pady=PADY, sticky=STICKY)
        self._entry_seconds.grid(row=0, column=3, padx=PADX, pady=PADY, sticky=STICKY)
        self._label_frames.grid(row=1, column=2, padx=PADX, pady=PADY, sticky=STICKY)
        self._entry_frames.grid(row=1, column=3, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_next_frame.grid(
            row=0, column=4, rowspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _wire_widgets(self) -> None:
        self._seconds.trace_add("write", callback=self._update_skip_time)
        self._frames.trace_add("write", callback=self._update_skip_time)

    def _update_skip_time(self, name: str, other: str, mode: str) -> None:
        self._viewmodel.update_skip_time(self._seconds.get(), self._frames.get())
