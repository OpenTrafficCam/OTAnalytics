from tkinter.ttk import Treeview
from typing import Any

from customtkinter import CTkButton, CTkFrame

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.plugin_ui.customtkinter_gui.button import StatefulButton
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.treeview_template import TreeviewTemplate


class FrameSections(CTkFrame):
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
        self.treeview = TreeviewSections(viewmodel=self._viewmodel, master=self)
        self.button_add = CTkButton(
            master=self, text="Add", command=self._viewmodel.add_section
        )
        self.button_edit_geometry = StatefulButton(
            master=self,
            text="Edit geometry",
            command=self._viewmodel.edit_section_geometry,
            viewmodel_setter=self._viewmodel.set_button_edit_section_geometry,
            state="disabled",
        )
        self.button_edit_metadata = StatefulButton(
            master=self,
            text="Edit metadata",
            command=self._viewmodel.edit_section_metadata,
            viewmodel_setter=self._viewmodel.set_button_edit_section_metadata,
            state="disabled",
        )
        self.button_remove = StatefulButton(
            master=self,
            text="Remove",
            command=self._viewmodel.remove_sections,
            viewmodel_setter=self._viewmodel.set_button_remove_section,
            state="disabled",
        )

    def _place_widgets(self) -> None:
        self.treeview.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_add.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_edit_geometry.grid(
            row=2, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_edit_metadata.grid(
            row=3, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_remove.grid(row=4, column=0, padx=PADX, pady=PADY, sticky=STICKY)


class TreeviewSections(TreeviewTemplate, Treeview):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        self._viewmodel = viewmodel
        super().__init__(**kwargs)
        self.bind("<ButtonRelease-2>", self._on_deselect)
        self.bind("<<TreeviewSelect>>", self._on_select)
        self._define_columns()
        self.configure(selectmode="extended")
        self._introduce_to_viewmodel()
        self.update_items()

    def _define_columns(self) -> None:
        self["columns"] = "Section"
        self.column(column="#0", width=0)
        self.column(column="Section", anchor="center", width=150, minwidth=40)
        self["displaycolumns"] = "Section"

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_treeview_sections(self)

    def _notify_viewmodel_about_selected_item_ids(
        self, line_section_ids: list[str]
    ) -> None:
        self._viewmodel.set_selected_section_ids(line_section_ids)

    def update_items(self) -> None:
        self.delete(*self.get_children())
        item_ids = [section.id.id for section in self._viewmodel.get_all_sections()]
        self.add_items(item_ids=item_ids)
