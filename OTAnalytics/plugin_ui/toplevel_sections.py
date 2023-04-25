from typing import Any

from customtkinter import CTkButton, CTkEntry, CTkLabel, CTkToplevel

from OTAnalytics.domain.section import ID, RELATIVE_OFFSET_COORDINATES
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_ui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.frame_bbox_offset import FrameBboxOffset


class ToplevelSections(CTkToplevel):
    def __init__(
        self,
        title: str,
        initial_position: tuple[int, int],
        input_values: dict | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title(title)
        # TODO: Get default values elsewhere!
        self.input_values: dict = (
            {
                ID: "",
                RELATIVE_OFFSET_COORDINATES: {
                    EventType.SECTION_ENTER.serialize(): {"x": 0.5, "y": 0.5},
                    "section-leave": {"x": 0.5, "y": 0.5},
                },
            }
            if input_values is None
            else input_values
        )
        self.protocol("WM_DELETE_WINDOW", self.close)
        self._initial_position = initial_position
        self._get_widgets()
        self._place_widgets()
        self._set_initial_position()
        self._set_focus()
        self._set_close_on_return_key()

    def _get_widgets(self) -> None:
        self.label_name = CTkLabel(master=self, text="Name:")
        self.entry_name = CTkEntry(master=self, width=180)
        self.entry_name.insert(0, self.input_values[ID])

        self.frame_bbox_offset = FrameBboxOffset(
            master=self,
            relative_offset_coordinates_enter=self.input_values[
                RELATIVE_OFFSET_COORDINATES
            ][EventType.SECTION_ENTER.serialize()],
        )

        self.button_ok = CTkButton(master=self, text="Ok", command=self.close)

    def _place_widgets(self) -> None:
        self.label_name.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="E")
        self.entry_name.grid(row=0, column=1, padx=PADX, pady=PADY, sticky="W")
        self.frame_bbox_offset.grid(
            row=1, column=0, columnspan=2, padx=PADX, sticky=STICKY
        )
        self.button_ok.grid(
            row=3, column=0, columnspan=3, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _set_initial_position(self) -> None:
        x, y = self._initial_position
        self.geometry(f"+{x+10}+{y+10}")

    def _set_focus(self) -> None:
        self.entry_name.focus_set()

    def _set_close_on_return_key(self) -> None:
        self.entry_name.bind("<Return>", self.close)

    def close(self, event: Any = None) -> None:
        self.input_values[ID] = self.entry_name.get()
        self.input_values[RELATIVE_OFFSET_COORDINATES][
            EventType.SECTION_ENTER.serialize()
        ] = self.frame_bbox_offset.get_relative_offset_coordintes_enter()
        self.destroy()
        self.update()

    def get_metadata(self) -> dict:
        self.wait_window()
        return self.input_values
