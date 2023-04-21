from abc import abstractmethod
from tkinter.ttk import Treeview
from typing import Optional


class AbstractTreeviewSections(Treeview):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def update_selection(self, section_id: Optional[str]) -> None:
        pass

    @abstractmethod
    def update_sections(self) -> None:
        pass
