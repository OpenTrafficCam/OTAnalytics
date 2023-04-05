from abc import ABC, abstractmethod


class EventHandler(ABC):
    @abstractmethod
    def attach_observer(self, observer: "CanvasObserver") -> None:
        pass

    @abstractmethod
    def detach_observer(self, observer: "CanvasObserver") -> None:
        pass


class CanvasObserver(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """

    def attach_to(self, event_handler: EventHandler) -> None:
        event_handler.attach_observer(self)

    def detach_from(self, event_handler: EventHandler) -> None:
        event_handler.detach_observer(self)

    @abstractmethod
    def update(self, coordinates: tuple[int, int], event_type: str) -> None:
        """
        Receive update from subject.
        """
        pass
