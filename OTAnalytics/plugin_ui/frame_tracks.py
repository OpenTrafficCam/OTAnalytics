from tkinter import DoubleVar
from typing import Any

from customtkinter import CTkButton, CTkEntry, CTkLabel

from OTAnalytics.adapter_ui.abstract_tracks_frame import AbstractTracksFrame
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.constants import PADX, PADY, STICKY


class TracksFrame(AbstractTracksFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_tracks_frame(self)

    def _get_widgets(self) -> None:
        self.label = CTkLabel(master=self, text="Tracks")
        self.button_load_tracks = CTkButton(
            master=self, text="Load tracks", command=self._viewmodel.load_tracks
        )
        self._offset_x = DoubleVar()
        self._offset_y = DoubleVar()
        self._label_offset = CTkLabel(master=self, text="Offset")
        self._label_offset_x = CTkLabel(master=self, text="X")
        self._label_offset_y = CTkLabel(master=self, text="Y")
        vcmd = self.register(self._validate_offset)
        self._text_offset_x = CTkEntry(
            master=self,
            textvariable=self._offset_x,
            validate="all",
            validatecommand=(vcmd, "%P"),
        )
        self._text_offset_y = CTkEntry(
            master=self,
            textvariable=self._offset_y,
            validate="all",
            validatecommand=(vcmd, "%P"),
        )
        self.button_update_offset = CTkButton(
            master=self,
            text="Update Plot",
            command=self._on_change_offset,
        )
        current_track_offset = self._viewmodel.get_track_offset()
        if current_track_offset:
            self.update_offset(*current_track_offset)

    def _validate_offset(self, value: str) -> bool:
        try:
            as_number = float(value)
            return 0 <= as_number <= 1
        except ValueError:
            return False

    def update_offset(self, new_offset_x: float, new_offset_y: float) -> None:
        self._offset_x.set(new_offset_x)
        self._offset_y.set(new_offset_y)

    def _place_widgets(self) -> None:
        self.label.grid(
            row=0, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_load_tracks.grid(
            row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_offset.grid(
            row=2, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self._label_offset_x.grid(row=3, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self._label_offset_y.grid(row=4, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self._text_offset_x.grid(row=3, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self._text_offset_y.grid(row=4, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_update_offset.grid(
            row=5, column=1, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _on_change_offset(self) -> None:
        self._viewmodel.set_track_offset(self._offset_x.get(), self._offset_y.get())
