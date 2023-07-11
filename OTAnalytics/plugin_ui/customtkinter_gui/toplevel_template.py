from abc import ABC, abstractmethod
from typing import Any

from customtkinter import CTkFrame, CTkToplevel

from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, tk_events
from OTAnalytics.plugin_ui.customtkinter_gui.utility_widgets import FrameOkCancel


class FrameContent(CTkFrame, ABC):
    @abstractmethod
    def set_focus(self) -> None:
        raise NotImplementedError("NotImplementedError")


class ToplevelTemplate(CTkToplevel, ABC):
    def __init__(
        self,
        title: str,
        initial_position: tuple[int, int],
        ok_text: str = "Ok",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title(title)
        self._ok_text = ok_text
        self._canceled: bool = False
        self._get_widgets()
        self._place_widgets()
        self._set_ok_cancel_bindings()
        self._set_initial_position(initial_position)
        self._set_focus()

    def _set_initial_position(self, initial_position: tuple[int, int]) -> None:
        x, y = initial_position
        x0 = x - (self.winfo_width() // 2)
        y0 = y - (self.winfo_height() // 2)
        self.geometry(f"+{x0+10}+{y0+10}")

    def _set_focus(self) -> None:
        self.attributes("-topmost", 1)
        self.after(0, lambda: self.lift())
        self._frame_content.set_focus()

    @abstractmethod
    def _create_frame_content(self, master: Any) -> FrameContent:
        raise NotImplementedError

    def _get_frame_footer(self) -> None:
        self._frame_footer = FrameOkCancel(
            master=self,
            on_ok=self._on_ok,
            on_cancel=self._on_cancel,
            ok_text=self._ok_text,
        )

    def _get_widgets(self) -> None:
        self._frame_content = self._create_frame_content(master=self)
        self._get_frame_footer()

    def _place_widgets(self) -> None:
        self._frame_content.pack(padx=PADX, pady=PADY)
        self._frame_footer.pack(padx=PADX, pady=PADY)

    def _set_ok_cancel_bindings(self) -> None:
        self.bind(tk_events.RETURN_KEY, self._on_ok)
        self.bind(tk_events.KEYPAD_RETURN_KEY, self._on_ok)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.bind(tk_events.ESCAPE_KEY, self._on_cancel)

    @abstractmethod
    def _on_ok(self, event: Any) -> None:
        raise NotImplementedError

    def _on_cancel(self, event: Any = None) -> None:
        self._canceled = True
        self._close()

    def _close(self) -> None:
        self.destroy()
        self.update()
