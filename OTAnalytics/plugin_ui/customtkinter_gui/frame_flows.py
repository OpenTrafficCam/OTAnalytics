import asyncio
import tkinter
from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkScrollbar

from OTAnalytics.adapter_ui.text_resources import ColumnResource, ColumnResources
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain.flow import Flow
from OTAnalytics.plugin_ui.customtkinter_gui.abstract_ctk_frame import AbstractCTkFrame
from OTAnalytics.plugin_ui.customtkinter_gui.constants import (
    PADX,
    PADY,
    STATE_DISABLED,
    STICKY,
)
from OTAnalytics.plugin_ui.customtkinter_gui.treeview_template import TreeviewTemplate


class FrameFlows(AbstractCTkFrame):
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
        self._set_button_state_categories()
        self._set_initial_button_states()
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
        self.button_add = CTkButton(master=self, text="Add", command=self._add_flow)
        self.button_generate = CTkButton(
            master=self, text="Generate", command=self._viewmodel.generate_flows
        )
        self.button_edit = CTkButton(
            master=self,
            text="Properties",
            command=self._edit_selected_flow,
        )
        self.button_remove = CTkButton(
            master=self, text="Remove", command=self._viewmodel.remove_flows
        )

    def _place_widgets(self) -> None:
        self.treeview.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        self._treeview_scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self._frame_tree.grid(
            row=0, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_add.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_generate.grid(row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_edit.grid(
            row=2, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_remove.grid(
            row=3, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _add_flow(self) -> None:
        asyncio.run(self._viewmodel.add_flow())

    def _edit_selected_flow(self) -> None:
        asyncio.run(self._viewmodel.edit_selected_flow())

    def _set_button_state_categories(self) -> None:
        self._general_buttons: list[CTkButton] = []
        self._add_buttons = [
            self.button_add,
            self.button_generate,
        ]
        self._single_item_buttons = [
            self.button_edit,
        ]
        self._multiple_items_buttons = [
            self.button_remove,
        ]

    def _set_initial_button_states(self) -> None:
        self.set_enabled_general_buttons(True)
        self.set_enabled_add_buttons(False)
        self.set_enabled_change_single_item_buttons(False)
        self.set_enabled_change_multiple_items_buttons(False)

    def get_general_buttons(self) -> list[CTkButton]:
        return self._general_buttons

    def get_add_buttons(self) -> list[CTkButton]:
        return self._add_buttons

    def get_single_item_buttons(self) -> list[CTkButton]:
        return self._single_item_buttons

    def get_multiple_items_buttons(self) -> list[CTkButton]:
        return self._multiple_items_buttons

    def _set_enabled_buttons(self, buttons: list[CTkButton], enabled: bool) -> None:
        super()._set_enabled_buttons(buttons, enabled)
        if len(list(self._viewmodel.get_all_flows())) > 0:
            self.button_generate.configure(state=STATE_DISABLED)


COLUMN_FLOW = "Flow"


class TreeviewFlows(TreeviewTemplate):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        self._viewmodel = viewmodel
        super().__init__(**kwargs)
        self._introduce_to_viewmodel()
        self.update_items()

    def _define_columns(self) -> None:
        columns = [COLUMN_FLOW]
        self["columns"] = columns
        self.column(column="#0", width=0, stretch=False)
        self.column(column=COLUMN_FLOW, anchor="center", width=150, minwidth=40)
        self["displaycolumns"] = columns

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_treeview_flows(self)

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        self._viewmodel.set_selected_flow_ids(ids)

    def _on_double_click(self, event: Any) -> None:
        asyncio.run(self._viewmodel.edit_selected_flow())

    def update_items(self) -> None:
        self.delete(*self.get_children())
        tracks_assigned_to_each_flow = (
            self._viewmodel.get_tracks_assigned_to_each_flow()
        )
        flows = []
        for flow in self._viewmodel.get_all_flows():
            flows.append(
                self.__to_resource(flow, tracks_assigned_to_each_flow[flow.id])
            )
        item_ids = ColumnResources(
            sorted(flows),
            lookup_column=COLUMN_FLOW,
        )
        self.add_items(item_ids=item_ids)

    @staticmethod
    def __to_resource(flow: Flow, tracks_assigned: int) -> ColumnResource:
        values = {COLUMN_FLOW: f"({tracks_assigned}) {flow.name}"}
        return ColumnResource(id=flow.id.id, values=values)
