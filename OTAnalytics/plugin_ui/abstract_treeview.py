from abc import abstractmethod
from tkinter.ttk import Treeview


class AbstractTreeviewSections(Treeview):
    @abstractmethod
    def introduce_to_viewmodel(self) -> None:
        pass
