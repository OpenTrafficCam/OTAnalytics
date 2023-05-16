from abc import ABC, abstractmethod


class EventHandler(ABC):
    @abstractmethod
    def attach_observer(self, observer: "CanvasObserver") -> None:
        raise NotImplementedError

    @abstractmethod
    def detach_observer(self, observer: "CanvasObserver") -> None:
        raise NotImplementedError


class CanvasObserver(ABC):
    def attach_to(self, event_handler: EventHandler) -> None:
        event_handler.attach_observer(self)

    def detach_from(self, event_handler: EventHandler) -> None:
        event_handler.detach_observer(self)

    @abstractmethod
    def update(
        self, coordinates: tuple[int, int], event_type: str, key: str | None
    ) -> None:
        """Receives and processes updates from canvas event handler"""
        raise NotImplementedError
