from abc import ABC, abstractmethod


class SectionGeometryBuilder(ABC):
    pass


class SectionGeometryPainter(ABC):
    @abstractmethod
    def draw_section(
        self, tag: str, id: str, start: tuple[int, int], end: tuple[int, int]
    ) -> None:
        raise NotImplementedError


class SectionGeometryUpdater(ABC):
    @abstractmethod
    def update_section(
        self, id: str, start: tuple[int, int], end: tuple[int, int]
    ) -> None:
        raise NotImplementedError


class SectionGeometryDeleter(ABC):
    @abstractmethod
    def delete_sections(self, tag_or_id: str) -> None:
        raise NotImplementedError


class TreeviewUpdater(ABC):
    @abstractmethod
    def list_items(self) -> None:
        raise NotImplementedError
