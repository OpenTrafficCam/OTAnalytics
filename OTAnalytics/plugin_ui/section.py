from abc import ABC, abstractmethod


class SectionGeometryBuilder(ABC):
    pass


class SectionGeometryDrawer(ABC):
    @abstractmethod
    def draw_section(
        self, tag: str, id: str, point0: tuple[int, int], point1: tuple[int, int]
    ) -> None:
        raise NotImplementedError


class SectionGeometryUpdater(ABC):
    @abstractmethod
    def update_section(
        self, id: str, point0: tuple[int, int], point1: tuple[int, int]
    ) -> None:
        raise NotImplementedError


class SectionGeometryDeleter(ABC):
    @abstractmethod
    def delete_sections(self, tag_or_id: str) -> None:
        raise NotImplementedError
