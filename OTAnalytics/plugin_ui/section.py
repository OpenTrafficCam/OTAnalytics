from abc import ABC, abstractmethod


class SectionBuilder(ABC):
    pass


class SectionDrawer(ABC):
    @abstractmethod
    def draw_section(
        self, tag: str, id: str, point0: tuple[int, int], point1: tuple[int, int]
    ) -> None:
        pass


class SectionUpdater(ABC):
    @abstractmethod
    def update_section(
        self, id: str, point0: tuple[int, int], point1: tuple[int, int]
    ) -> None:
        pass


class SectionDeleter(ABC):
    @abstractmethod
    def delete_sections(self, tag_or_id: str) -> None:
        pass
