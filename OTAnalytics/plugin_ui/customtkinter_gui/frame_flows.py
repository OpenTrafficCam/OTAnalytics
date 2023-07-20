import tkinter
from tkinter.ttk import Treeview
from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkScrollbar

from OTAnalytics.adapter_ui.abstract_frame_flows import AbstractFrameFlows
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain.flow import Flow
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import get_widget_position
from OTAnalytics.plugin_ui.customtkinter_gui.treeview_template import (
    IdResource,
    TreeviewTemplate,
)


class FrameFlows(AbstractFrameFlows):
    def __init__(
        self,
        viewmodel: ViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._get_widgets()
        self._place_widgets()
        self.introduce_to_viewmodel()

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_flows_frame(self)

    def _get_widgets(self) -> None:
        self._frame_tree = CTkFrame(master=self)
        self.treeview = TreeviewFlows(
            viewmodel=self._viewmodel, master=self._frame_tree
        )
        self._treeview_scrollbar = CTkScrollbar(
            master=self._frame_tree, command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=self._treeview_scrollbar.set)
        self.button_add = CTkButton(
            master=self, text="Add", command=self._viewmodel.add_flow
        )
        self.button_generate = CTkButton(
            master=self, text="Generate", command=self._viewmodel.generate_flows
        )
        self.button_edit = CTkButton(
            master=self,
            text="Properties",
            command=self._viewmodel.edit_flow,
        )
        self.button_remove = CTkButton(
            master=self, text="Remove", command=self._viewmodel.remove_flows
        )
        self._action_buttons = [self.button_add, self.button_edit, self.button_remove]

    def _place_widgets(self) -> None:
        self.treeview.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        self._treeview_scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self._frame_tree.grid(
            row=0, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_add.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_generate.grid(row=2, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_edit.grid(row=3, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_remove.grid(row=4, column=0, padx=PADX, pady=PADY, sticky=STICKY)

    def action_buttons(self) -> list[CTkButton]:
        return self._action_buttons

    def enable_remove_button(self) -> None:
        self._enable_button(self.button_remove)

    def disable_remove_button(self) -> None:
        self._disable_button(self.button_remove)

    def enable_edit_button(self) -> None:
        self._enable_button(self.button_edit)

    def disable_edit_button(self) -> None:
        self._disable_button(self.button_edit)

    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        x, y = get_widget_position(self, offset=offset)
        return x, y


class TreeviewFlows(TreeviewTemplate, Treeview):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        self._viewmodel = viewmodel
        super().__init__(**kwargs)
        self._define_columns()
        self._introduce_to_viewmodel()
        self.update_items()

    def _define_columns(self) -> None:
        self["columns"] = "Flow"
        self.column(column="#0", width=0, stretch=False)
        self.column(column="Flow", anchor="center", width=150, minwidth=40)
        self["displaycolumns"] = "Flow"

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_treeview_flows(self)

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        self._viewmodel.set_selected_flow_ids(ids)

    def update_items(self) -> None:
        self.delete(*self.get_children())
        item_ids = [
            self.__to_id_resource(flow) for flow in self._viewmodel.get_all_flows()
        ]
        self.add_items(item_ids=sorted(item_ids))

    def __to_id_resource(self, flow: Flow) -> IdResource:
        return IdResource(id=flow.id.id, name=flow.name)
