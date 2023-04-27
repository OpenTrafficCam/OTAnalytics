from typing import Any

from customtkinter import CTkButton, CTkEntry, CTkLabel, CTkOptionMenu, CTkToplevel

from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import InfoBox

DISTANCE = "Distance"
START_SECTION = "Start section"
END_SECTION = "End section"


class ToplevelFlows(CTkToplevel):
    def __init__(
        self,
        title: str,
        initial_position: tuple[int, int],
        section_ids: list[str],
        input_values: dict | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title(title)
        self._section_ids = section_ids
        self.input_values: dict = (
            {
                START_SECTION: "",
                END_SECTION: "",
                DISTANCE: 0,
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
        self.label_section_start = CTkLabel(master=self, text="First section:")
        self.dropdown_section_start = CTkOptionMenu(
            master=self, width=180, values=self._section_ids
        )
        self.dropdown_section_start.set(self.input_values[START_SECTION])
        self.label_section_end = CTkLabel(master=self, text="Second section:")
        self.dropdown_section_end = CTkOptionMenu(
            master=self, width=180, values=self._section_ids
        )
        self.dropdown_section_end.set(self.input_values[END_SECTION])
        self.label_distance = CTkLabel(master=self, text="Distance [m]:")
        self.entry_distance = CTkEntry(
            master=self,
            width=180,
            validate="key",
            validatecommand=(self.register(self._is_float_above_zero), "%P"),
        )
        self.entry_distance.insert(0, self.input_values[DISTANCE])

        self.button_ok = CTkButton(master=self, text="Ok", command=self.close)

    def _place_widgets(self) -> None:
        self.label_section_start.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="E")
        self.dropdown_section_start.grid(
            row=1, column=1, padx=PADX, pady=PADY, sticky="W"
        )
        self.label_section_end.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="E")
        self.dropdown_section_end.grid(
            row=2, column=1, padx=PADX, pady=PADY, sticky="W"
        )
        self.label_distance.grid(row=3, column=0, padx=PADX, pady=PADY, sticky="E")
        self.entry_distance.grid(row=3, column=1, padx=PADX, pady=PADY, sticky="W")
        self.button_ok.grid(
            row=4, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _set_initial_position(self) -> None:
        x, y = self._initial_position
        self.geometry(f"+{x+10}+{y+10}")

    def _set_focus(self) -> None:
        self.entry_distance.focus_set()

    def _set_close_on_return_key(self) -> None:
        self.entry_distance.bind("<Return>", self.close)

    def close(self, event: Any = None) -> None:
        if not self._sections_are_valid():
            return
        self.input_values[START_SECTION] = self.dropdown_section_start.get()
        self.input_values[END_SECTION] = self.dropdown_section_end.get()
        self.input_values[DISTANCE] = self.entry_distance.get()
        self.destroy()
        self.update()

    def _is_float_above_zero(self, entry_value: Any) -> bool:
        try:
            float_value = float(entry_value)
        except Exception:
            return False
        return float_value >= 0

    def _sections_are_valid(self) -> bool:
        section_start = self.dropdown_section_start.get()
        section_end = self.dropdown_section_end.get()
        sections = [section_start, section_end]
        position = (self.winfo_x(), self.winfo_y())
        if "" in [section_start, section_end]:
            InfoBox(
                message="Please choose both a start and an end section!",
                initial_position=position,
            )
            return False
        elif section_start == section_end:
            InfoBox(
                message="Start and end section have to be different!",
                initial_position=position,
            )
            return False
        else:
            for section in sections:
                if section not in self._section_ids:
                    InfoBox(
                        message="Start and end section have to be valid sections!",
                        initial_position=position,
                    )
                    return False
        return True

    def get_data(self) -> dict:
        self.wait_window()
        return self.input_values
