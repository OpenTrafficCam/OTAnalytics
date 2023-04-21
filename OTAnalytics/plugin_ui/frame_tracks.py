from pathlib import Path
from tkinter import DoubleVar
from tkinter.filedialog import askopenfilename
from typing import Any, Optional

from customtkinter import CTkButton, CTkEntry, CTkFrame, CTkLabel

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain.geometry import RelativeOffsetCoordinate
from OTAnalytics.plugin_ui.constants import PADX, PADY, STICKY


class FrameTracks(CTkFrame):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()

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
            command=self._change_offset,
        )
        self.application.track_view_state.track_offset.register(self._update_offset)
        self._update_offset(self.application.track_view_state.track_offset.get())

    def _validate_offset(self, value: str) -> bool:
        try:
            as_number = float(value)
            return 0 <= as_number <= 1
        except ValueError:
            return False

    def _update_offset(self, new_offset: Optional[RelativeOffsetCoordinate]) -> None:
        if offset := new_offset:
            self._offset_x.set(offset.x)
            self._offset_y.set(offset.y)

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

    def _load_tracks_in_file(self) -> None:
        track_file = askopenfilename(
            title="Load tracks file", filetypes=[("tracks file", "*.ottrk")]
        )
        print(f"Tracks file to load: {track_file}")
        self.application.add_tracks_of_file(track_file=Path(track_file))

    def _change_offset(self) -> None:
        self.application.track_view_state.track_offset.set(self._offset_from_text())

    def _offset_from_text(self) -> RelativeOffsetCoordinate:
        x = self._offset_x.get()
        y = self._offset_y.get()
        return RelativeOffsetCoordinate(x, y)
