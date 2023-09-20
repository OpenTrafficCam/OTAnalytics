from unittest.mock import Mock, call

import pytest

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


class TestAutoIncrementingProgressbar:
    def test(self) -> None:
        numbers = [1, 2, 3]
        counter = Mock(spec=Counter)
        counter.get_value.return_value = 1
        notify = Mock()
        progressbar = AutoIncrementingProgressbar(numbers, counter, notify)
        result = [elem for elem in progressbar]
        assert result == numbers
        assert counter.increment.call_args_list == [call(1), call(1), call(1)]
        assert notify.call_count == len(numbers)

    @pytest.mark.parametrize("step_percentage", [-1, 0, 101])
    def test_validation(self, step_percentage: int) -> None:
        numbers = [1, 2, 3]
        counter = Mock(spec=Counter)
        notify = Mock()
        with pytest.raises(ValueError):
            AutoIncrementingProgressbar(numbers, counter, notify, step_percentage)


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
