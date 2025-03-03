from typing import Any

from customtkinter import CTkButton, CTkLabel, CTkToplevel

from OTAnalytics.adapter_ui.info_box import InfoBox
from OTAnalytics.adapter_ui.message_box import MessageBox
from OTAnalytics.plugin_ui.customtkinter_gui.constants import (
    PADX,
    PADY,
    STICKY,
    tk_events,
)


class CtkInfoBox(CTkToplevel, InfoBox):
    @property
    def canceled(self) -> bool:
        return self._canceled

    def __init__(
        self,
        message: str,
        initial_position: tuple[int, int],
        title: str = "Information",
        show_cancel: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title(title)
        self.message = message
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind(tk_events.ESCAPE_KEY, self._on_cancel)
        self._canceled = False
        self._initial_position = initial_position
        self._show_cancel = show_cancel
        self._get_widgets()
        self._place_widgets()
        self._set_initial_position()
        self._set_focus()
        self._set_close_on_return_key()
        self.wait_window()

    def _get_widgets(self) -> None:
        self.label_name = CTkLabel(master=self, text=self.message)
        self.button_ok = CTkButton(master=self, text="Ok", command=self.close)
        self.button_cancel = CTkButton(
            master=self, text="Cancel", command=self._on_cancel
        )

    def _place_widgets(self) -> None:
        if self._show_cancel:
            self.label_name.grid(
                row=0, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
            )
            self.button_ok.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY)
            self.button_cancel.grid(
                row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY
            )
        else:
            self.label_name.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
            self.button_ok.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY)

    def _set_focus(self) -> None:
        self.attributes("-topmost", 1)
        self.after(0, lambda: self.button_ok.focus_set())

    def _set_close_on_return_key(self) -> None:
        self.button_ok.bind(tk_events.RETURN_KEY, self.close)
        self.button_ok.bind(tk_events.KEYPAD_RETURN_KEY, self.close)

    def _set_initial_position(self) -> None:
        x, y = self._initial_position
        self.geometry(f"+{x}+{y}")

    def close(self, event: Any = None) -> None:
        self.destroy()
        self.update()

    def _on_cancel(self, event: Any = None) -> None:
        self._canceled = True
        self.close(event)


class MinimalInfoBox(CTkToplevel, MessageBox):
    """InfoBox popup without title bar."""

    def __init__(
        self,
        message: str,
        initial_position: tuple[int, int],
        title: str = "Information",
        show_cancel: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title(title)
        self.message = message
        self.canceled = False
        self._initial_position = initial_position
        self._show_cancel = show_cancel
        self._get_widgets()
        self._place_widgets()
        self._set_initial_position()
        self._set_focus()
        # Not using self.overrideredirect to remove title bar here since
        # unknown behaviour of that method errors when trying to
        # draw as second Section
        self.tk.call("wm", "overrideredirect", self._w, True)

    def _get_widgets(self) -> None:
        self._label_message = CTkLabel(master=self, text=self.message)
        self.button_cancel = CTkButton(
            master=self, text="Cancel", command=self._on_cancel
        )

    def _place_widgets(self) -> None:
        self._label_message.grid(
            row=0, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        if self._show_cancel:
            self.button_cancel.grid(
                row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY
            )

    def _set_focus(self) -> None:
        self.attributes("-topmost", 1)

    def _set_initial_position(self) -> None:
        x, y = self._initial_position
        self.geometry(f"+{x}+{y}")

    def close(self, event: Any = None) -> None:
        self.destroy()
        self.update()

    def _on_cancel(self, event: Any = None) -> None:
        self.canceled = True
        self.close(event)

    def update_message(self, message: str) -> None:
        self._label_message.configure(text=message)
        self.update()
