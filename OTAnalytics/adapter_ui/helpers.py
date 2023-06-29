from abc import ABC, abstractmethod


class WidgetPositionProvider(ABC):
    @abstractmethod
    def get_position(self, offset: tuple[float, float]) -> tuple[int, int]:
        raise NotImplementedError
