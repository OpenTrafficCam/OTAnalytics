import asyncio
from dataclasses import dataclass
from unittest.mock import Mock, call

import pytest

from OTAnalytics.application.progress import (
    AutoIncrementingProgressbar,
    Cancellation,
    ManualIncrementingProgressbar,
    ProgressState,
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


class TestCancellation:
    """#Requirement https://openproject.platomo.de/wp/10281"""

    def test_is_not_cancelled_before_cancel(self) -> None:
        target = Cancellation()

        assert target.is_cancelled is False

    def test_is_cancelled_after_cancel(self) -> None:
        target = Cancellation()

        target.cancel()

        assert target.is_cancelled is True

    def test_cancelling_twice_keeps_it_cancelled(self) -> None:
        target = Cancellation()

        target.cancel()
        target.cancel()

        assert target.is_cancelled is True

    async def test_wait_returns_once_cancelled(self) -> None:
        target = Cancellation()
        waiting = asyncio.ensure_future(target.wait())
        await asyncio.sleep(0)

        assert not waiting.done()

        target.cancel()
        await asyncio.wait_for(waiting, timeout=1)


@dataclass
class ProgressStateGiven:
    counter: Counter
    on_change: Mock


def create_given() -> ProgressStateGiven:
    return ProgressStateGiven(counter=SimpleCounter(), on_change=Mock())


def create_target(
    given: ProgressStateGiven, description: str = "Downloading", total: int = 4
) -> ProgressState:
    return ProgressState(
        description=description,
        unit="files",
        total=total,
        counter=given.counter,
        on_change=given.on_change,
    )


class TestProgressState:
    """#Requirement https://openproject.platomo.de/wp/10281"""

    def test_starts_empty(self) -> None:
        given = create_given()
        target = create_target(given)

        assert target.fraction == 0.0
        assert target.message == "Downloading 0 / 4 files"
        assert target.current_item == ""
        assert target.finished is False

    def test_completing_an_item_advances_the_count(self) -> None:
        given = create_given()
        target = create_target(given)

        target.complete("first.mp4")

        assert target.fraction == 0.25
        assert target.message == "Downloading 1 / 4 files"
        assert target.current_item == "first.mp4"

    def test_counts_completions_arriving_out_of_order(self) -> None:
        given = create_given()
        target = create_target(given)

        target.complete("fourth.mp4")
        target.complete("first.mp4")
        target.complete("third.mp4")

        assert target.message == "Downloading 3 / 4 files"
        assert target.current_item == "third.mp4"

    def test_is_finished_once_every_item_completed(self) -> None:
        given = create_given()
        target = create_target(given, total=2)

        target.complete("first.mp4")
        assert target.finished is False

        target.complete("second.mp4")
        assert target.finished is True
        assert target.fraction == 1.0

    def test_notifies_on_every_completion(self) -> None:
        given = create_given()
        target = create_target(given, total=2)

        target.complete("first.mp4")
        target.complete("second.mp4")

        assert given.on_change.call_count == 2

    def test_notify_reports_progress_made_through_the_counter(self) -> None:
        given = create_given()
        target = create_target(given)

        given.counter.increment(2)
        target.notify()

        assert target.message == "Downloading 2 / 4 files"
        given.on_change.assert_called_once()

    def test_an_empty_sequence_is_finished_from_the_start(self) -> None:
        given = create_given()
        target = create_target(given, total=0)

        assert target.finished is True
        assert target.fraction == 1.0
