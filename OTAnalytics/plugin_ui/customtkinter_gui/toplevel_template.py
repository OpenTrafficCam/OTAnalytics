from abc import ABC, abstractmethod
from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkToplevel

from OTAnalytics.application.config import ON_MAC
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, tk_events


class ToplevelTemplate(CTkToplevel, ABC):
    def __init__(
        self,
        initial_position: tuple[int, int],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._get_frame_ok_cancel()
        self._set_ok_cancel_bindings()
        self._set_initial_position(initial_position)
        self._set_focus()

    def _set_initial_position(self, initial_position: tuple[int, int]) -> None:
        x, y = initial_position
        self.geometry(f"+{x+10}+{y+10}")

    def _get_frame_ok_cancel(self) -> None:
        self.frame_ok_cancel = CTkFrame(master=self)
        self.button_ok = CTkButton(
            master=self.frame_ok_cancel, text="Ok", command=self._on_ok
        )
        self.button_cancel = CTkButton(
            master=self.frame_ok_cancel, text="Cancel", command=self._on_cancel
        )
        if ON_MAC:
            ok_column = 1
            cancel_column = 0
        else:
            ok_column = 0
            cancel_column = 1
        self.button_ok.grid(row=0, column=ok_column, padx=PADX, pady=PADY)
        self.button_cancel.grid(row=0, column=cancel_column, padx=PADX, pady=PADY)

    def _set_ok_cancel_bindings(self) -> None:
        self.bind(tk_events.RETURN_KEY, self._on_ok)
        self.bind(tk_events.KEYPAD_RETURN_KEY, self._on_ok)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind(tk_events.ESCAPE_KEY, self._on_cancel)

    @abstractmethod
    def _on_ok(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _on_cancel(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def _set_focus(self) -> None:
        raise NotImplementedError
