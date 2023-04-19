from typing import Any

from customtkinter import CTkButton, CTkEntry, CTkLabel, CTkToplevel

from OTAnalytics.plugin_ui.constants import PADX, PADY, STICKY


class ToplevelSections(CTkToplevel):
    def __init__(
        self, title: str, input_values: dict | None = None, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.title(title)
        self.input_values: dict = {"name": ""} if input_values is None else input_values
        self.protocol("WM_DELETE_WINDOW", self.close)
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.label_name = CTkLabel(master=self, text="Name:")
        self.entry_name = CTkEntry(master=self)
        self.entry_name.insert(0, self.input_values["name"])
        self.button_ok = CTkButton(master=self, text="Ok", command=self.close)

    def _place_widgets(self) -> None:
        self.label_name.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="E")
        self.entry_name.grid(row=0, column=1, padx=PADX, pady=PADY, sticky="W")
        self.button_ok.grid(
            row=1, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )

    def close(self) -> None:
        self.input_values["name"] = self.entry_name.get()
        self.destroy()
        self.update()

    def show(self) -> dict:
        self.wait_window()
        return self.input_values
