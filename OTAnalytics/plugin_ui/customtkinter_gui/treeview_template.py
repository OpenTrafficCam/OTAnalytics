from abc import abstractmethod
from dataclasses import dataclass
from tkinter.ttk import Treeview
from typing import Any

from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.helpers import WidgetPositionProvider
from OTAnalytics.plugin_ui.customtkinter_gui.constants import tk_events
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import get_widget_position


@dataclass(frozen=True, order=True)
class IdResource:
    id: str
    name: str


class TreeviewTemplate(AbstractTreeviewInterface, WidgetPositionProvider, Treeview):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(show="tree", selectmode="none", **kwargs)
        self.bind(tk_events.RIGHT_BUTTON_UP, self._on_deselect)
        self.bind(tk_events.LEFT_BUTTON_UP, self._on_single_select)
        self.bind(tk_events.MULTI_SELECT_SINGLE, self._on_single_multi_select)
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

    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        x, y = get_widget_position(self, offset=offset)
        return x, y

    def add_items(self, item_ids: list[IdResource]) -> None:
        for id in item_ids:
            self.insert(parent="", index="end", iid=id.id, text="", values=[id.name])

    def _on_deselect(self, event: Any) -> None:
        self._deselect_all()

    def _deselect_all(self) -> None:
        self.selection_set([])
        self._notify_viewmodel_about_selected_item_ids([])

    def _on_single_select(self, event: Any) -> None:
        current_selection = self.focus()
        self.selection_set(current_selection)
        self._notify_viewmodel_about_selected_item_ids([current_selection])

    def _on_single_multi_select(self, event: Any) -> None:
        current_selection = self.focus()
        self.selection_toggle(current_selection)
        self._notify_viewmodel_about_selected_item_ids(self.get_current_selection())

    def get_current_selection(self) -> list[str]:
        return list(self.selection())
