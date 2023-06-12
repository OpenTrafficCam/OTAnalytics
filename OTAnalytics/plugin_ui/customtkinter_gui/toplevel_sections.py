from typing import Any

from customtkinter import CTkButton, CTkEntry, CTkLabel, CTkToplevel

from OTAnalytics.adapter_ui.default_values import RELATIVE_SECTION_OFFSET
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain.section import ID, NAME, RELATIVE_OFFSET_COORDINATES
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_ui.customtkinter_gui.constants import (
    PADX,
    PADY,
    STICKY,
    tk_events,
)
from OTAnalytics.plugin_ui.customtkinter_gui.frame_bbox_offset import FrameBboxOffset
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import InfoBox


class ToplevelSections(CTkToplevel):
    def __init__(
        self,
        title: str,
        viewmodel: ViewModel,
        initial_position: tuple[int, int],
        input_values: dict | None = None,
        show_offset: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title(title)
        self._viewmodel = viewmodel
        # TODO: Get default values elsewhere!
        self.input_values: dict = (
            {
                ID: "",
                NAME: "",
                RELATIVE_OFFSET_COORDINATES: {
                    EventType.SECTION_ENTER.serialize(): {
                        "x": RELATIVE_SECTION_OFFSET.x,
                        "y": RELATIVE_SECTION_OFFSET.y,
                    },
                },
            }
            if input_values is None
            else input_values
        )
        self._show_offset = show_offset
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self._initial_position = initial_position
        self._get_widgets()
        self._place_widgets()
        self._set_initial_position()
        self._set_focus()
        self._set_close_on_return_key()

    def _get_widgets(self) -> None:
        self.label_name = CTkLabel(master=self, text="Name:")
        self.entry_name = CTkEntry(master=self, width=180)
        self.entry_name.insert(0, self.input_values[NAME])

        self.frame_bbox_offset = FrameBboxOffset(
            master=self,
            frame_heading="Bounding Box offset for enter-events:",
            relative_offset_coordinates=self.input_values[RELATIVE_OFFSET_COORDINATES][
                EventType.SECTION_ENTER.serialize()
            ],
        )

        self.button_ok = CTkButton(master=self, text="Ok", command=self.close)

    def _place_widgets(self) -> None:
        self.label_name.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="E")
        self.entry_name.grid(row=0, column=1, padx=PADX, pady=PADY, sticky="W")
        if self._show_offset:
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
        self.after(0, lambda: self.lift())
        self.after(0, lambda: self.entry_name.focus_set())

    def _set_close_on_return_key(self) -> None:
        self.entry_name.bind(tk_events.RETURN_KEY, self.close)
        self.entry_name.bind(tk_events.KEYPAD_RETURN_KEY, self.close)

    def close(self, event: Any = None) -> None:
        if not self._name_is_valid():
            return
        self.input_values[NAME] = self.entry_name.get()
        self.input_values[RELATIVE_OFFSET_COORDINATES][
            EventType.SECTION_ENTER.serialize()
        ] = self.frame_bbox_offset.get_relative_offset_coordintes()
        self.destroy()
        self.update()

    def _name_is_valid(self) -> bool:
        if not self._viewmodel.is_section_name_valid(self.entry_name.get()):
            position = (self.winfo_x(), self.winfo_y())
            InfoBox(
                message="Please choose a name for the section!",
                initial_position=position,
            )
            return False
        return True

    def get_metadata(self) -> dict:
        self.wait_window()
        return self.input_values
