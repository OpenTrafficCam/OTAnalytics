from typing import Any
from unittest.mock import Mock

from OTAnalytics.domain.observer import Subject


class TestSubject:
    def test_register(self) -> None:
        observer = Mock()
        other_observer = Mock()

        subject = Subject[Any]()
        subject.register(observer)
        subject.register(other_observer)
        assert subject._observers == [observer, other_observer]
        subject.register(observer)
        assert subject._observers == [observer, other_observer]

    def test_notify(self) -> None:
        observer = Mock()
        other_observer = Mock()

        subject = Subject[Any]()
        subject.register(observer)
        subject.register(other_observer)

        value = Mock()
        subject.notify(value)

        observer.assert_called_once_with(value)
        other_observer.assert_called_once_with(value)
