from tkinter import Widget
from typing import Any, Optional, Sequence

from customtkinter import CTkLabel, CTkProgressBar, CTkToplevel

from OTAnalytics.adapter_ui.abstract_progressbar_popup import (
    AbstractPopupProgressbar,
    ProgressbarPopupBuilder,
)
from OTAnalytics.application.progress import AutoIncrementingProgressbar, SimpleCounter
from OTAnalytics.domain.progress import (
    Counter,
    ProgressbarBuilder,
    ProgressbarBuildError,
)
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import get_widget_position


class InvalidRelativeProgressError(Exception):
    pass


class ProgressbarPopupTemplate(AbstractPopupProgressbar, CTkToplevel):
    def __init__(
        self,
        counter: Counter,
        unit: str,
        total: int,
        initial_position: tuple[int, int],
        description: str,
        title: str = "",
        **kwargs: Any,
    ) -> None:
        self._unit = unit
        self._total = total
        self._current_progress = counter
        self._close = False if self._total else True

        super().__init__(**kwargs)
        self.title(title)
        self._description = description
        self._get_widgets()
        self._place_widgets()
        self._set_focus()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.tk.call("wm", "overrideredirect", self._w, True)
        self._set_initial_position(initial_position)
        self.update_progress()

    def _set_initial_position(self, initial_position: tuple[int, int]) -> None:
        x, y = initial_position
        x0 = x - (self.winfo_width() // 2)
        y0 = y - (self.winfo_height() // 2)
        self.geometry(f"+{x0}+{y0}")

    def _set_focus(self) -> None:
        self.after(0, lambda: self.lift())

    def _get_widgets(self) -> None:
        self._label_description = CTkLabel(master=self, text=self._description)
        self._progressbar_message = CTkLabel(master=self, text="")
        self._progressbar = CTkProgressBar(master=self, height=15)
        self._progressbar.set(self._current_progress.get_value())

    def _place_widgets(self) -> None:
        self._label_description.pack(padx=PADX, pady=PADY)
        self._progressbar_message.pack(padx=PADX, pady=PADY)
        self._progressbar.pack(padx=PADX, pady=PADY)

    def _update_progress(self) -> None:
        if not self._total:
            self.destroy()
            return

        percent = self._current_progress.get_value() / self._total
        message = (
            f"{self._current_progress.get_value()} of " f"{self._total} {self._unit}"
        )
        if percent >= 1:
            self._close = True
            self.destroy()
        else:
            self._progressbar_message.configure(text=message)
            self._progressbar.set(value=percent)
            self.update()

    def _on_cancel(self) -> None:
        pass


class PullingProgressbarPopup(ProgressbarPopupTemplate):
    def update_progress(self) -> None:
        self._update_progress()


class PollingProgressbarPopup(ProgressbarPopupTemplate):
    def update_progress(self) -> None:
        self._update_progress()
        if not self._close:
            self.master.after(1000, self.update_progress)


class PullingProgressbarPopupBuilder(ProgressbarPopupBuilder):
    def __init__(self) -> None:
        self._master: Optional[Widget] = None

    def add_widget(self, widget: Widget) -> None:
        self._master = widget

    def build(self) -> AbstractPopupProgressbar:
        if not self._master:
            raise ProgressbarBuildError(
                f"Missing master widget in {ProgressbarBuilder.__name__}"
            )

        if not self._counter:
            raise ProgressbarBuildError(
                f"Missing counter in {ProgressbarBuilder.__name__}"
            )
        if self._total is None:
            raise ProgressbarBuildError(
                f"Missing total in {ProgressbarBuilder.__name__}"
            )

        initial_position = get_widget_position(self._master)
        return PullingProgressbarPopup(
            counter=self._counter,
            unit=self._unit,
            total=self._total,
            initial_position=initial_position,
            description=self._description,
        )


class PollingProgressbarPopupBuilder(ProgressbarPopupBuilder):
    def __init__(self) -> None:
        self._master: Optional[Widget] = None

    def add_widget(self, widget: Widget) -> None:
        self._master = widget

    def build(self) -> PollingProgressbarPopup:
        if not self._master:
            raise ProgressbarBuildError(
                f"Missing master widget in {ProgressbarBuilder.__name__}"
            )

        if not self._counter:
            raise ProgressbarBuildError(
                f"Missing counter in {ProgressbarBuilder.__name__}"
            )
        if self._total is None:
            raise ProgressbarBuildError(
                f"Missing total in {ProgressbarBuilder.__name__}"
            )

        initial_position = get_widget_position(self._master)
        return PollingProgressbarPopup(
            counter=self._counter,
            unit=self._unit,
            total=self._total,
            initial_position=initial_position,
            description=self._description,
        )


class PullingProgressbarBuilder(ProgressbarBuilder):
    def __init__(self, popup_builder: ProgressbarPopupBuilder) -> None:
        self._popup_builder = popup_builder

    def __call__(
        self, sequence: Sequence, description: str, unit: str
    ) -> AutoIncrementingProgressbar:
        counter = SimpleCounter()
        self._popup_builder.add_counter(counter)
        self._popup_builder.add_description(description)
        self._popup_builder.add_unit(unit)
        self._popup_builder.add_total(len(sequence))
        popup = self._popup_builder.build()
        return AutoIncrementingProgressbar(sequence, counter, popup.update_progress)
