from typing import Any
from unittest.mock import Mock

import pytest

from OTAnalytics.domain.observer import Subject


class TestSubject:
    def test_register(self, observer: Mock, other_observer: Mock) -> None:
        subject = self.create_target()
        subject.register(observer)
        subject.register(other_observer)

        assert subject._observers == [observer, other_observer]
        subject.register(observer)
        assert subject._observers == [observer, other_observer]

    def test_notify(self, observer: Mock, other_observer: Mock, message: Mock) -> None:
        subject = self.create_target()
        subject.register(observer)
        subject.register(other_observer)

        subject.notify(message)

        subject.unregister(observer)
        subject.notify(message)

        observer.assert_called_once_with(message)
        assert other_observer.call_count == 2
        other_observer.assert_called_with(message)

    def create_target(self) -> Subject[Any]:
        return Subject[Any]()


@pytest.fixture
def observer() -> Mock:
    return Mock()


@pytest.fixture
def other_observer() -> Mock:
    return Mock()


@pytest.fixture
def message() -> Mock:
    return Mock()
