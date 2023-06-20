from typing import Any

from customtkinter import CTkLabel, CTkProgressBar, CTkToplevel

from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY


class InvalidRelativeProgressError(Exception):
    pass


class ToplevelProgress(CTkToplevel):
    def __init__(
        self,
        title: str,
        initial_position: tuple[int, int],
        initial_message: str,
        initial_progress: float = 0.0,
        indeterminate_progress_mode: float = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.title(title)
        self._initial_message = initial_message
        self._initial_progress = initial_progress
        self._get_widgets()
        self._place_widgets()
        self._set_initial_position(initial_position)
        self._set_focus()
        self.update()

    def _set_initial_position(self, initial_position: tuple[int, int]) -> None:
        x, y = initial_position
        self.geometry(f"+{x+10}+{y+10}")

    def _set_focus(self) -> None:
        self.after(0, lambda: self.lift())

    def _get_widgets(self) -> None:
        self._label_message = CTkLabel(master=self, text=self._initial_message)
        self._progressbar = CTkProgressBar(master=self, height=15)
        self._progressbar.set(self._initial_progress)

    def _place_widgets(self) -> None:
        self._label_message.pack(padx=PADX, pady=PADY)
        self._progressbar.pack(padx=PADX, pady=PADY)

    def proceed_to(self, percent: float, message: str | None = None) -> None:
        print(percent)
        if percent < 0 or percent > 1:
            raise InvalidRelativeProgressError
        elif percent == 1:
            self.destroy()
            self.mainloop()
        else:
            self._label_message.configure(text=message)
            self._progressbar.set(value=percent)
            self.update()
