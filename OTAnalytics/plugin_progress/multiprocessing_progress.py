from multiprocessing.managers import ValueProxy
from threading import Lock
from typing import Sequence

from OTAnalytics.adapter_ui.abstract_progressbar_popup import ProgressbarPopupBuilder
from OTAnalytics.application.progress import ManualIncrementingProgressbar
from OTAnalytics.domain.progress import Counter, ProgressbarBuilder


class ProcessSafeCounter(Counter):
    def __init__(self, value: ValueProxy[int], lock: Lock) -> None:
        self._value = value
        self._lock = lock

    def increment(self, value: int = 1) -> None:
        with self._lock:
            self._value.value += value

    def reset(self) -> None:
        with self._lock:
            self._value.set(0)

    def get_value(self) -> int:
        return self._value.get()


class ProcessSafePollingProgressbarBuilder(ProgressbarBuilder):
    def __init__(
        self,
        popup_builder: ProgressbarPopupBuilder,
        counter_value: ValueProxy,
        lock: Lock,
    ) -> None:
        self._popup_builder = popup_builder
        self._counter_value = counter_value
        self._lock = lock

    def __call__(
        self, sequence: Sequence, description: str, unit: str
    ) -> ManualIncrementingProgressbar:
        counter = ProcessSafeCounter(self._counter_value, self._lock)
        progressbar = ManualIncrementingProgressbar(sequence, counter, None)
        self._popup_builder.add_counter(counter)
        self._popup_builder.add_description(description)
        self._popup_builder.add_unit(unit)
        self._popup_builder.add_total(len(sequence))
        self._popup_builder.build()
        return progressbar
