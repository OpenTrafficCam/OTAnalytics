from multiprocessing import Manager, Pool, cpu_count
from multiprocessing.managers import SyncManager
from typing import Iterator
from unittest.mock import Mock

import pytest

from OTAnalytics.adapter_ui.abstract_progressbar_popup import ProgressbarPopupBuilder
from OTAnalytics.domain.progress import Counter
from OTAnalytics.plugin_progress.multiprocessing_progress import (
    ProcessSafeCounter,
    ProcessSafePollingProgressbarBuilder,
)
from tests.conftest import YieldFixture


@pytest.fixture
def manager() -> YieldFixture[SyncManager]:
    manager = Manager()
    yield manager
    manager.shutdown()


@pytest.fixture
def counter(manager: SyncManager) -> ProcessSafeCounter:
    lock = manager.Lock()
    counter_value = manager.Value("i", 0)
    return ProcessSafeCounter(counter_value, lock)


def increment(counter: Counter) -> None:
    counter.increment(1)


class TestProcessSafeCounter:
    def test(self, counter: ProcessSafeCounter) -> None:
        assert counter.get_value() == 0

        process_count = cpu_count()

        with Pool(processes=process_count) as pool:
            for _ in range(0, process_count):
                pool.apply_async(func=increment, args=(counter,))
            pool.close()
            pool.join()
        assert counter.get_value() == process_count
        counter.reset()
        assert counter.get_value() == 0


class TestProcessSafePollingProgressbarBuilder:
    def test(self, manager: SyncManager) -> None:
        lock = manager.Lock()
        counter_value = manager.Value("i", 0)
        popup_builder = Mock(spec=ProgressbarPopupBuilder)
        sequence = [1, 2, 3]
        desc = "My Track"
        unit = "Tracks"

        builder = ProcessSafePollingProgressbarBuilder(
            popup_builder, counter_value, lock
        )
        progressbar = builder(sequence, desc, unit)
        assert isinstance(progressbar, Iterator)
        popup_builder.add_counter.assert_called_once()
        popup_builder.add_description.assert_called_once_with(desc)
        popup_builder.add_unit.assert_called_once_with(unit)
        popup_builder.build.assert_called_once()
