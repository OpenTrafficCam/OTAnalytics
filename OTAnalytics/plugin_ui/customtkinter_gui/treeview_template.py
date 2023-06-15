from abc import abstractmethod
from dataclasses import dataclass
from tkinter.ttk import Treeview
from typing import Any

from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.plugin_ui.customtkinter_gui.constants import tk_events


@dataclass(frozen=True, order=True)
class IdResource:
    id: str
    name: str


class TreeviewTemplate(AbstractTreeviewInterface, Treeview):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(show="tree", selectmode="none", **kwargs)
        self.bind(tk_events.RIGHT_BUTTON_UP, self._on_deselect)
        self.bind(tk_events.LEFT_BUTTON_UP, self._on_select)
        self._define_columns()
        self._introduce_to_viewmodel()
        self.update_items()

    # TODO: add property viewmodel

    @abstractmethod
    def _define_columns(self) -> None:
        raise NotImplementedError

    def update_selected_items(self, item_ids: list[str]) -> None:
        if item_ids == self.get_current_selection():
            return

        if item_ids:
            self.selection_set(item_ids)
        else:
            self._deselect_all()

    def get_position(self) -> tuple[int, int]:
        return self.winfo_rootx(), self.winfo_rooty()

    def add_items(self, item_ids: list[IdResource]) -> None:
        for id in item_ids:
            self.insert(parent="", index="end", iid=id.id, text="", values=[id.name])

    def _on_deselect(self, event: Any) -> None:
        self._deselect_all()

    def _deselect_all(self) -> None:
        self.selection_set([])
        self._notify_viewmodel_about_selected_item_ids([])

    def _on_select(self, event: Any) -> None:
        current_selection: str = self.focus()
        self.selection_toggle(current_selection)
        item_ids = self.get_current_selection()
        self._notify_viewmodel_about_selected_item_ids(item_ids)

    def get_current_selection(self) -> list[str]:
        return list(self.selection())
