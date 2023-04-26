from abc import abstractmethod
from typing import Optional


class AbstractTreeviewSections:
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def update_selection(self, section_id: Optional[str]) -> None:
        pass

    @abstractmethod
    def update_sections(self) -> None:
        pass
