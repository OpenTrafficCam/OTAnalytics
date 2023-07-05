from tkinter import Widget
from typing import Any, Iterator, Optional, Sequence

from customtkinter import CTkLabel, CTkProgressBar, CTkToplevel

from OTAnalytics.domain.progress import (
    Progressbar,
    ProgressbarBuilder,
    ProgressbarBuildError,
)
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import get_widget_position


class InvalidRelativeProgressError(Exception):
    pass


class PopupProgressbar(Progressbar, CTkToplevel):
    def __init__(
        self,
        sequence: Sequence,
        unit: str,
        initial_position: tuple[int, int],
        initial_message: str,
        initial_progress: float = 0.0,
        title: str = "",
        **kwargs: Any,
    ) -> None:
        self.__sequence = sequence
        self.__unit = unit
        self.__current_progress = 0
        self.__current_iterator = iter(sequence)

        super().__init__(**kwargs)
        self.title(title)
        self._initial_message = initial_message
        self._initial_progress = initial_progress
        self._get_widgets()
        self._place_widgets()
        self._set_focus()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.overrideredirect(True)  # TODO: Test on Windows
        self.update()
        self._set_initial_position(initial_position)

    def _set_initial_position(self, initial_position: tuple[int, int]) -> None:
        x, y = initial_position
        x0 = x - (self.winfo_width() // 2)
        y0 = y - (self.winfo_height() // 2)
        self.geometry(f"+{x0}+{y0}")

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

    def _on_cancel(self) -> None:
        pass

    def __iter__(self) -> Iterator:
        self.__current_progress = 0
        self.__current_iterator = iter(self.__sequence)
        return self

    def __next__(self) -> Any:
        try:
            next_element = next(self.__current_iterator)
            self.__update_progress()
            return next_element
        except StopIteration:
            self.__update_progress()
            raise StopIteration

    def __update_progress(self) -> None:
        len_sequence = len(self.__sequence)
        progress_in_percent = self.__current_progress / len_sequence
        self.proceed_to(
            progress_in_percent,
            message=f"{self.__current_progress} of {len_sequence} "
            f"{self.__unit} processed.",
        )
        self.__current_progress += 1


class PopupProgressbarBuilder(ProgressbarBuilder):
    def __init__(self) -> None:
        self._master: Optional[Widget] = None

    def add_widget(self, widget: Widget) -> None:
        self._master = widget

    def __call__(self, sequence: Sequence, description: str, unit: str) -> Progressbar:
        if not self._master:
            raise ProgressbarBuildError(
                f"Missing master widget in {ProgressbarBuilder.__name__}"
            )

        initial_position = self._get_position(self._master)
        return PopupProgressbar(
            master=self._master,
            sequence=sequence,
            unit=unit,
            initial_position=initial_position,
            initial_message=description,
        )

    def _get_position(self, widget: Widget) -> tuple[int, int]:
        return get_widget_position(widget)
