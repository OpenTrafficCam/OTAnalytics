from abc import ABC
from typing import Generic, TypeVar

OBSERVER = TypeVar("OBSERVER")


class Registrable(ABC, Generic[OBSERVER]):
    """A convenience class for subjects that ensures the uniqueness of registered
    observers while retaining insertion order.
    """

    def __init__(self) -> None:
        self._observers: list[OBSERVER] = []

    def register(self, observer: OBSERVER) -> None:
        """Listen to changes of subject extending from this class.

        Args:
            observer (OBSERVER): the observer to be registered
        """
        new_observers = self._observers.copy()
        new_observers.append(observer)
        self._observers = list(dict.fromkeys(new_observers))
