from typing import Generator
from unittest.mock import Mock, call

from OTAnalytics.application.progress import (
    AutoIncrementingProgressbar,
    ManualIncrementingProgressbar,
    SimpleCounter,
)
from OTAnalytics.domain.progress import Counter


class TestSimpleCounter:
    def test(self) -> None:
        counter = SimpleCounter()
        assert counter.get_value() == 0
        counter.increment()
        assert counter.get_value() == 1
        counter.reset()
        assert counter.get_value() == 0


def mock_counter() -> Generator:
    current = 0
    while True:
        current = current + 1
        yield current


class TestAutoIncrementingProgressbar:
    def test(self) -> None:
        numbers = [1, 2, 3]
        counter = Mock(spec=Counter)
        counter.get_value.side_effect = mock_counter()
        notify = Mock()
        progressbar = AutoIncrementingProgressbar(numbers, counter, notify)
        result = [elem for elem in progressbar]
        assert result == numbers
        assert counter.increment.call_args_list == [call(1), call(1), call(1)]
        assert notify.call_count == len(numbers)


class TestManualIncrementingProgressbar:
    def test(self) -> None:
        numbers = [1, 2, 3]
        counter = Mock(spec=Counter)
        notify = Mock()
        progressbar = ManualIncrementingProgressbar(numbers, counter, notify)
        result = [elem for elem in progressbar]
        assert result == numbers
        counter.assert_not_called()
        assert notify.call_count == len(numbers)
