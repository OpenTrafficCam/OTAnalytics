from abc import abstractmethod
from tkinter.ttk import Treeview


class AbstractTreeviewSections(Treeview):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass

    @abstractmethod
    def add_section(self, id: str, name: str) -> None:
        pass

    @abstractmethod
    def get_selected_section(self) -> str:
        pass
