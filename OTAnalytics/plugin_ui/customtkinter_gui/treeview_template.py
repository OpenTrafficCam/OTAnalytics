from abc import abstractmethod
from dataclasses import dataclass
from tkinter.ttk import Treeview
from typing import Any, Literal

from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.helpers import WidgetPositionProvider
from OTAnalytics.plugin_ui.customtkinter_gui.constants import tk_events
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import get_widget_position


@dataclass(frozen=True, order=True)
class IdResource:
    """
    Represents a row in a treeview with an id and a dict of values to be shown.
    The dicts keys represent the columns and the values represent the cell values.
    """

    id: str
    values: dict[str, str]


class TreeviewTemplate(AbstractTreeviewInterface, WidgetPositionProvider, Treeview):
    def __init__(
        self,
        show: Literal["tree", "headings", "tree headings", ""] = "tree",
        **kwargs: Any
    ) -> None:
        super().__init__(selectmode="none", show=show, **kwargs)
        self.bind(tk_events.RIGHT_BUTTON_UP, self._on_deselect)
        self.bind(tk_events.LEFT_BUTTON_UP, self._on_single_select)
        self.bind(tk_events.MULTI_SELECT_SINGLE, self._on_single_multi_select)
        self.bind(tk_events.LEFT_BUTTON_DOUBLE, self._on_double_click)
        self._columns = self._define_columns()
        self._introduce_to_viewmodel()
        self.update_items()

    # TODO: add property viewmodel

    @abstractmethod
    def _define_columns(self) -> list[str]:
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
        # TODO: @martinbaerwolff 1update insert to new IdResource.values dict
        for id in item_ids:
            cell_values = tuple(id.values[column] for column in self._columns)
            self.insert(parent="", index="end", iid=id.id, text="", values=cell_values)

    def _on_deselect(self, event: Any) -> None:
        self._deselect_all()

    def _deselect_all(self) -> None:
        self.selection_set([])
        self._notify_viewmodel_about_selected_item_ids([])

    def _on_single_select(self, event: Any) -> None:
        current_selection = self.__get_current_selection()
        self.selection_set(current_selection)
        self._notify_viewmodel_about_selected_item_ids(current_selection)

    def __get_current_selection(self) -> list[str]:
        current_selection = self.focus()
        return [current_selection] if current_selection else []

    def _on_single_multi_select(self, event: Any) -> None:
        current_selection = self.focus()
        self.selection_toggle(current_selection)
        self._notify_viewmodel_about_selected_item_ids(self.get_current_selection())

    @abstractmethod
    def _on_double_click(self, event: Any) -> None:
        raise NotImplementedError

    def get_current_selection(self) -> list[str]:
        return list(self.selection())
