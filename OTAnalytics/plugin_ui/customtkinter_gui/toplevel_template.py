from abc import ABC, abstractmethod
from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkToplevel

from OTAnalytics.application.config import ON_MAC
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY


class ToplevelTemplate(CTkToplevel, ABC):
    def __init__(
        self,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._get_frame_ok_cancel()

    def _get_frame_ok_cancel(self) -> None:
        self.frame_ok_cancel = CTkFrame(master=self)
        self.button_ok = CTkButton(
            master=self.frame_ok_cancel, text="Ok", command=self.close
        )
        self.button_cancel = CTkButton(
            master=self.frame_ok_cancel, text="Cancel", command=self.cancel
        )
        if ON_MAC:
            ok_column = 1
            cancel_column = 0
        else:
            ok_column = 0
            cancel_column = 1
        self.button_ok.grid(row=0, column=ok_column, padx=PADX, pady=PADY)
        self.button_cancel.grid(row=0, column=cancel_column, padx=PADX, pady=PADY)

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def cancel(self) -> None:
        raise NotImplementedError
