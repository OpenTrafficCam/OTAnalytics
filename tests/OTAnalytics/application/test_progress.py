from unittest.mock import Mock, call

from OTAnalytics.application.progress import NotifyableProgressbar, SimpleCounter
from OTAnalytics.domain.progress import Counter


class TestSimpleCounter:
    def test(self) -> None:
        counter = SimpleCounter()
        assert counter.get_value() == 0
        counter.increment()
        assert counter.get_value() == 1
        counter.reset()
        assert counter.get_value() == 0


class TestNotifyableProgressbar:
    def test(self) -> None:
        numbers = [1, 2, 3]
        counter = Mock(spec=Counter)
        notify = Mock()
        progressbar = NotifyableProgressbar(numbers, counter, notify)
        result = [elem for elem in progressbar]
        assert result == numbers
        counter.increment.call_args = [call(1), call(1), call(1)]
        assert notify.call_count == len(numbers) + 1
