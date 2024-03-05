import tkinter
from typing import Any

from customtkinter import CTkButton, CTkEntry, CTkLabel, ThemeManager

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.abstract_ctk_frame import AbstractCTkFrame
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.style import COLOR_RED


class FrameVideoControl(AbstractCTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._is_initialized = False
        self._viewmodel = viewmodel
        self.default_border_color = ThemeManager.theme["CTkEntry"]["border_color"]
        self._seconds = tkinter.StringVar(value=str(viewmodel.get_skip_seconds()))
        self._frames = tkinter.StringVar(value=str(viewmodel.get_skip_frames()))
        self._get_widgets()
        self._place_widgets()
        self._wire_widgets()
        self.introduce_to_viewmodel()
        self._is_initialized = True

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_video_control_frame(self)

    def _get_widgets(self) -> None:
        self._button_next_frame = CTkButton(
            master=self,
            text=">",
            command=self._viewmodel.next_frame,
        )
        self._button_previous_frame = CTkButton(
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
        self._entry_seconds = CTkEntry(
            master=self,
            textvariable=self._seconds,
            validate="key",
            validatecommand=(self.register(self._validate_int), "%P", "%W"),
        )
        self._entry_frames = CTkEntry(
            master=self,
            textvariable=self._frames,
            validate="key",
            validatecommand=(self.register(self._validate_int), "%P", "%W"),
        )

    def _validate_int(self, value: Any, widget_name: str) -> bool:
        if not self._is_initialized:
            return True
        widget: CTkEntry = self.nametowidget(widget_name).master
        try:
            int(value)
            widget.configure(border_color=self.default_border_color)
        except ValueError:
            widget.configure(border_color=COLOR_RED)
        return True

    def _place_widgets(self) -> None:
        PADY = 10
        self._button_previous_frame.grid(
            row=0, column=1, rowspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_seconds.grid(row=0, column=2, padx=PADX, pady=PADY, sticky=STICKY)
        self._entry_seconds.grid(row=0, column=3, padx=PADX, pady=PADY, sticky=STICKY)
        self._label_frames.grid(row=1, column=2, padx=PADX, pady=PADY, sticky=STICKY)
        self._entry_frames.grid(row=1, column=3, padx=PADX, pady=PADY, sticky=STICKY)
        self._button_next_frame.grid(
            row=0, column=4, rowspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _wire_widgets(self) -> None:
        self._seconds.trace_add("write", callback=self._update_skip_time)
        self._frames.trace_add("write", callback=self._update_skip_time)

    def get_general_buttons(self) -> list[CTkButton]:
        return [self._button_previous_frame, self._button_next_frame]

    def _update_skip_time(self, name: str, other: str, mode: str) -> None:
        try:
            self._viewmodel.update_skip_time(
                int(self._seconds.get()), int(self._frames.get())
            )
        except ValueError:
            pass
