from tkinter import E, StringVar, W
from typing import Any, Optional

from customtkinter import CTkButton, CTkEntry, CTkLabel, CTkOptionMenu, CTkToplevel

from OTAnalytics.plugin_ui.customtkinter_gui.constants import (
    PADX,
    PADY,
    STICKY,
    tk_events,
)
from OTAnalytics.plugin_ui.customtkinter_gui.messagebox import InfoBox
from OTAnalytics.plugin_ui.customtkinter_gui.treeview_template import IdResource

FLOW_ID = "Id"
FLOW_NAME = "Name"
START_SECTION = "Start section"
END_SECTION = "End section"
DISTANCE = "Distance"


class ToplevelFlows(CTkToplevel):
    def __init__(
        self,
        title: str,
        initial_position: tuple[int, int],
        section_ids: list[IdResource],
        input_values: dict | None = {},
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title(title)
        self._section_ids = section_ids
        self._section_name_to_id = self._create_section_name_to_id(section_ids)
        self._section_id_to_name = self._create_section_id_to_name(section_ids)
        self._current_name = StringVar()
        self.input_values: dict = self.__create_input_values(input_values)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self._initial_position = initial_position
        self.__set_initial_values()
        self._get_widgets()
        self._place_widgets()
        self._set_initial_position()
        self._set_focus()
        self._set_close_on_return_key()

    def _create_section_name_to_id(self, sections: list[IdResource]) -> dict[str, str]:
        return {resource.name: resource.id for resource in sections}

    def _create_section_id_to_name(self, sections: list[IdResource]) -> dict[str, str]:
        return {resource.id: resource.name for resource in sections}

    def __set_initial_values(self) -> None:
        self._current_name.set(self.input_values.get(FLOW_NAME, ""))

    def __create_input_values(self, input_values: Optional[dict]) -> dict:
        if input_values:
            return input_values
        return {
            FLOW_ID: "",
            FLOW_NAME: "",
            START_SECTION: "",
            END_SECTION: "",
            DISTANCE: 0,
        }

    def _get_widgets(self) -> None:
        self.label_id = CTkLabel(master=self, text="Name")
        self.entry_id = CTkEntry(
            master=self,
            width=180,
            textvariable=self._current_name,
        )
        self.label_section_start = CTkLabel(master=self, text="First section:")
        self.dropdown_section_start = CTkOptionMenu(
            master=self, width=180, values=self._section_names()
        )
        self.dropdown_section_start.set(self._get_start_section_name())
        self.label_section_end = CTkLabel(master=self, text="Second section:")
        self.dropdown_section_end = CTkOptionMenu(
            master=self, width=180, values=self._section_names()
        )
        self.dropdown_section_end.set(self._get_end_section_name())
        self.label_distance = CTkLabel(master=self, text="Distance [m]:")
        self.entry_distance = CTkEntry(
            master=self,
            width=180,
            validate="key",
            validatecommand=(self.register(self._is_float_above_zero), "%P"),
        )
        self.entry_distance.insert(0, self.input_values[DISTANCE])

        self.button_ok = CTkButton(master=self, text="Ok", command=self.close)

    def _section_names(self) -> list[str]:
        return [resource.name for resource in self._section_ids]

    def _get_end_section_name(self) -> str:
        _id = self.input_values[END_SECTION]
        return self._get_section_name_for_id(_id)

    def _get_section_name_for_id(self, name: str) -> str:
        return self._section_id_to_name.get(name, "")

    def _get_start_section_name(self) -> str:
        _id = self.input_values[START_SECTION]
        return self._get_section_name_for_id(_id)

    def _place_widgets(self) -> None:
        self.label_id.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=E)
        self.entry_id.grid(row=0, column=1, padx=PADX, pady=PADY, sticky=W)
        self.label_section_start.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=E)
        self.dropdown_section_start.grid(
            row=1, column=1, padx=PADX, pady=PADY, sticky=W
        )
        self.label_section_end.grid(row=2, column=0, padx=PADX, pady=PADY, sticky=E)
        self.dropdown_section_end.grid(row=2, column=1, padx=PADX, pady=PADY, sticky=W)
        self.label_distance.grid(row=3, column=0, padx=PADX, pady=PADY, sticky=E)
        self.entry_distance.grid(row=3, column=1, padx=PADX, pady=PADY, sticky=W)
        self.button_ok.grid(
            row=4, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _set_initial_position(self) -> None:
        x, y = self._initial_position
        self.geometry(f"+{x+10}+{y+10}")

    def _set_focus(self) -> None:
        self.after(0, lambda: self.lift())
        self.after(0, lambda: self.entry_distance.focus_set())

    def _set_close_on_return_key(self) -> None:
        self.entry_distance.bind(tk_events.RETURN_KEY, self.close)
        self.entry_distance.bind(tk_events.KEYPAD_RETURN_KEY, self.close)

    def close(self, event: Any = None) -> None:
        if not self._sections_are_valid():
            return
        self.input_values[FLOW_NAME] = self._current_name.get()
        self.input_values[START_SECTION] = self._get_start_section_id()
        self.input_values[END_SECTION] = self._get_end_section_id()
        self.input_values[DISTANCE] = self.entry_distance.get()
        self.destroy()
        self.update()

    def _get_end_section_id(self) -> str:
        name = self.dropdown_section_end.get()
        return self._get_section_id_for_name(name)

    def _get_section_id_for_name(self, name: str) -> str:
        return self._section_name_to_id.get(name, "")

    def _get_start_section_id(self) -> str:
        name = self.dropdown_section_start.get()
        return self._get_section_id_for_name(name)

    def _is_float_above_zero(self, entry_value: Any) -> bool:
        try:
            float_value = float(entry_value)
        except Exception:
            return False
        return float_value >= 0

    def _sections_are_valid(self) -> bool:
        section_start = self._get_start_section_id()
        section_end = self._get_end_section_id()
        sections = [section_start, section_end]
        position = (self.winfo_x(), self.winfo_y())
        if self._current_name.get() == "":
            InfoBox(
                message="Please choose a flow name!",
                initial_position=position,
            )
            return False
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
                if section not in [resource.id for resource in self._section_ids]:
                    InfoBox(
                        message="Start and end section have to be valid sections!",
                        initial_position=position,
                    )
                    return False
        return True

    def get_data(self) -> dict:
        self.wait_window()
        return self.input_values
