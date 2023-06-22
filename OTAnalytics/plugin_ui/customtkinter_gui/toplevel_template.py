from abc import ABC, abstractmethod
from typing import Any

from customtkinter import CTkToplevel

from OTAnalytics.plugin_ui.customtkinter_gui.constants import tk_events


class ToplevelTemplate(CTkToplevel, ABC):
    def __init__(
        self,
        title: str,
        initial_position: tuple[int, int],
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title(title)
        self._set_ok_cancel_bindings()
        self._set_initial_position(initial_position)

    def _set_initial_position(self, initial_position: tuple[int, int]) -> None:
        x, y = initial_position
        self.geometry(f"+{x+10}+{y+10}")

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
