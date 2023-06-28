from typing import Any, Callable

from customtkinter import CTkButton, CTkFrame

from OTAnalytics.application.config import ON_MAC
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY


class FrameOkCancel(CTkFrame):
    def __init__(
        self,
        on_ok: Callable[[Any], None],
        on_cancel: Callable[[Any], None],
        ok_text: str = "Ok",
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._on_ok = on_ok
        self._on_cancel = on_cancel
        self._ok_text = ok_text
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.button_ok = CTkButton(master=self, text=self._ok_text, command=self._on_ok)
        self.button_cancel = CTkButton(
            master=self, text="Cancel", command=self._on_cancel
        )

    def _place_widgets(self) -> None:
        if ON_MAC:
            ok_column = 1
            cancel_column = 0
        else:
            ok_column = 0
            cancel_column = 1
        self.button_ok.grid(row=0, column=ok_column, padx=PADX, pady=PADY)
        self.button_cancel.grid(row=0, column=cancel_column, padx=PADX, pady=PADY)
