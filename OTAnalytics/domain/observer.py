from typing import Callable, Generic, TypeVar

VALUE = TypeVar("VALUE")
OBSERVER = Callable[[VALUE], None]


class Subject(Generic[VALUE]):
    """Generic subject class to handle and notify observers.

    This class ensures that no duplicate observers can be registered.
    The order that registered observers are notified is dictated by the order they have
    been registered. Meaning, first to be registered is first to be notified.
    """

    def __init__(self) -> None:
        self._observers: list[OBSERVER] = []

    def register(self, observer: OBSERVER) -> None:
        """Listen to changes of the subject.

        Args:
            observer (OBSERVER): the observer to be registered. This must be a
                `Callable`.
        """
        new_observers = self._observers.copy()
        new_observers.append(observer)
        self._observers = list(dict.fromkeys(new_observers))

    def unregister(self, observer: OBSERVER) -> None:
        """Stop listening to changes of the subject.

        Args:
            observer (OBSERVER): the observer to be unregistered.
        """
        self._observers.remove(observer)

    def notify(self, value: VALUE) -> None:
        """Notifies observers about the list of tracks.

        Args:
            value (VALUE): value to notify the observer with.
        """
        [notify_observer(value) for notify_observer in self._observers]
