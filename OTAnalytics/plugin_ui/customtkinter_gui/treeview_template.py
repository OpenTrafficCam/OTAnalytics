from abc import abstractmethod
from tkinter.ttk import Treeview
from typing import Any, Optional

from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.plugin_ui.customtkinter_gui.constants import tk_events


class TreeviewTemplate(AbstractTreeviewInterface, Treeview):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(show="tree", selectmode="browse", **kwargs)
        self.bind(tk_events.RIGHT_BUTTON_UP, self._on_deselect)
        self.bind(tk_events.TREEVIEW_SELECT, self._on_select)
        self._define_columns()
        self._introduce_to_viewmodel()
        self.update_items()

    # TODO: add property viewmodel

    @abstractmethod
    def _define_columns(self) -> None:
        raise NotImplementedError

    def update_selected_items(self, item_id: Optional[str]) -> None:
        if item_id == self.get_current_selection():
            return

        if item_id:
            self.selection_set(item_id)
        else:
            self._deselect_all()

    def get_position(self) -> tuple[int, int]:
        return self.winfo_rootx(), self.winfo_rooty()

    def add_items(self, item_ids: list[str]) -> None:
        for id in item_ids:
            self.insert(parent="", index="end", iid=id, text="", values=[id])

    def _on_deselect(self, event: Any) -> None:
        self._deselect_all()

    def _deselect_all(self) -> None:
        for item in self.selection():
            self.selection_remove(item)

    def _on_select(self, event: Any) -> None:
        item_id = self.get_current_selection()
        self._notify_viewmodel_about_selected_item_id(item_id)

    def get_current_selection(self) -> Optional[str]:
        selection = self.selection()
        if len(selection) == 0:
            item_id = None
        elif len(selection) == 1:
            item_id = selection[0]
        else:
            raise ValueError("Only one item in the Treeview shall be selected")
        return item_id
