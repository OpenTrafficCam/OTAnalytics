from typing import Any, Sequence

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
        initial_message: str,
        initial_progress: float = 0.0,
        title: str = "",
        **kwargs: Any,
    ) -> None:
        self._unit = unit
        self._total = total
        self._current_progress = counter
        self._close = False

        super().__init__(**kwargs)
        self.title(title)
        self._initial_message = initial_message
        self._initial_progress = initial_progress
        self._get_widgets()
        self._place_widgets()
        self._set_focus()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.overrideredirect(True)  # TODO: Test on Windows
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
        self._label_description = CTkLabel(master=self, text=self._initial_message)
        self._label_message = CTkLabel(master=self, text="")
        self._progressbar = CTkProgressBar(master=self, height=15)
        self._progressbar.set(self._initial_progress)

    def _place_widgets(self) -> None:
        self._label_description.pack(padx=PADX, pady=PADY)
        self._label_message.pack(padx=PADX, pady=PADY)
        self._progressbar.pack(padx=PADX, pady=PADY)

    def _update_progress(self) -> None:
        percent = self._current_progress.get_value() / self._total
        # print(percent)
        message = (
            f"{self._current_progress.get_value()} of " f"{self._total} {self._unit}"
        )
        if percent >= 1:
            print("closed")
            self._close = True
            self.destroy()
        else:
            self._label_message.configure(text=message)
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
            print("Not closed yet")
            self.master.after(1000, self.update_progress)


class PullingProgressbarPopupBuilder(ProgressbarPopupBuilder):
    def build(self) -> AbstractPopupProgressbar:
        if not self._master:
            raise ProgressbarBuildError(
                f"Missing master widget in {ProgressbarBuilder.__name__}"
            )

        if not self._counter:
            raise ProgressbarBuildError(
                f"Missing counter in {ProgressbarBuilder.__name__}"
            )
        if not self._total:
            raise ProgressbarBuildError(
                f"Missing total in {ProgressbarBuilder.__name__}"
            )

        initial_position = get_widget_position(self._master)
        return PullingProgressbarPopup(
            counter=self._counter,
            unit=self._unit,
            total=self._total,
            initial_position=initial_position,
            initial_message=self._description,
        )


class PollingProgressbarPopupBuilder(ProgressbarPopupBuilder):
    def build(self) -> PollingProgressbarPopup:
        if not self._master:
            raise ProgressbarBuildError(
                f"Missing master widget in {ProgressbarBuilder.__name__}"
            )

        if not self._counter:
            raise ProgressbarBuildError(
                f"Missing counter in {ProgressbarBuilder.__name__}"
            )
        if not self._total:
            raise ProgressbarBuildError(
                f"Missing total in {ProgressbarBuilder.__name__}"
            )

        initial_position = get_widget_position(self._master)
        return PollingProgressbarPopup(
            counter=self._counter,
            unit=self._unit,
            total=self._total,
            initial_position=initial_position,
            initial_message=self._description,
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
        progressbar = AutoIncrementingProgressbar(
            sequence, counter, popup.update_progress
        )
        return progressbar
