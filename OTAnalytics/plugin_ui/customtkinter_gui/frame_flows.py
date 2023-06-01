from tkinter.ttk import Treeview
from typing import Any, Optional

from customtkinter import CTkButton, CTkFrame

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain.flow import Flow
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.treeview_template import (
    IdResource,
    TreeviewTemplate,
)


class FrameFlows(CTkFrame):
    def __init__(
        self,
        viewmodel: ViewModel,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._get_widgets()
        self._place_widgets()

    def _get_widgets(self) -> None:
        self.treeview = TreeviewFlows(viewmodel=self._viewmodel, master=self)
        self.button_add = CTkButton(
            master=self, text="Add", command=self._viewmodel.add_flow
        )
        self.button_edit = CTkButton(
            master=self,
            text="Edit",
            command=self._viewmodel.edit_flow,
        )
        self.button_remove = CTkButton(
            master=self, text="Remove", command=self._viewmodel.remove_flow
        )

    def _place_widgets(self) -> None:
        self.treeview.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_add.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_edit.grid(row=2, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_remove.grid(row=3, column=0, padx=PADX, pady=PADY, sticky=STICKY)


class TreeviewFlows(TreeviewTemplate, Treeview):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        self._viewmodel = viewmodel
        super().__init__(**kwargs)
        self._define_columns()
        self._introduce_to_viewmodel()
        self.update_items()

    def _define_columns(self) -> None:
        self["columns"] = "Flow"
        self.column(column="#0", width=0)
        self.column(column="Flow", anchor="center", width=150, minwidth=40)
        self["displaycolumns"] = "Flow"

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_treeview_flows(self)

    def _notify_viewmodel_about_selected_item_id(self, flow_id: Optional[str]) -> None:
        self._viewmodel.set_selected_flow_id(flow_id)

    def update_items(self) -> None:
        self.delete(*self.get_children())
        item_ids = [
            self.__to_id_resource(flow) for flow in self._viewmodel.get_all_flows()
        ]
        self.add_items(item_ids=sorted(item_ids))

    def __to_id_resource(self, flow: Flow) -> IdResource:
        return IdResource(id=flow.id.id, name=flow.name)
