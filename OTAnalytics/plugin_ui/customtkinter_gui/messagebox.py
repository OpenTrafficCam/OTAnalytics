from typing import Any

from customtkinter import CTkButton, CTkLabel, CTkToplevel

from OTAnalytics.plugin_ui.customtkinter_gui.constants import (
    PADX,
    PADY,
    STICKY,
    tk_events,
)


class InfoBox(CTkToplevel):
    def __init__(
        self,
        message: str,
        initial_position: tuple[int, int],
        title: str = "Information",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title(title)
        self.message = message
        self.protocol("WM_DELETE_WINDOW", self.close)
        self._initial_position = initial_position
        self._get_widgets()
        self._place_widgets()
        self._set_initial_position()
        self._set_focus()
        self._set_close_on_return_key()
        self.wait_window()

    def _get_widgets(self) -> None:
        self.label_name = CTkLabel(master=self, text=self.message)
        self.button_ok = CTkButton(master=self, text="Ok", command=self.close)

    def _place_widgets(self) -> None:
        self.label_name.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_ok.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY)

    def _set_focus(self) -> None:
        self.button_ok.focus_set()

    def _set_close_on_return_key(self) -> None:
        self.button_ok.bind(tk_events.RETURN_KEY, self.close)
        self.button_ok.bind(tk_events.KEYPAD_RETURN_KEY, self.close)

    def _set_initial_position(self) -> None:
        x, y = self._initial_position
        self.geometry(f"+{x}+{y}")

    def close(self, event: Any = None) -> None:
        self.destroy()
        self.update()
