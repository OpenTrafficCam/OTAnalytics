import asyncio
import tkinter
from tkinter import Listbox
from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkScrollbar

from OTAnalytics.adapter_ui.text_resources import (
    COLUMN_NAME,
    ColumnResource,
    ColumnResources,
)
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain.section import Section
from OTAnalytics.plugin_ui.customtkinter_gui.abstract_ctk_frame import AbstractCTkFrame
from OTAnalytics.plugin_ui.customtkinter_gui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.customtkinter_gui.treeview_template import TreeviewTemplate


class FrameSections(AbstractCTkFrame):
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
        self._viewmodel.set_sections_frame(self)

    def _get_widgets(self) -> None:
        self._frame_tree = CTkFrame(master=self)
        self.treeview = TreeviewSections(
            viewmodel=self._viewmodel, master=self._frame_tree
        )
        self._treeview_scrollbar = CTkScrollbar(
            master=self._frame_tree, command=self.treeview.yview
        )
        self.treeview.configure(yscrollcommand=self._treeview_scrollbar.set)
        self.button_add_line = CTkButton(
            master=self, text="Add line", command=self._viewmodel.add_line_section
        )
        self.button_add_area = CTkButton(
            master=self, text="Add area", command=self._viewmodel.add_area_section
        )
        self.button_edit_geometry = CTkButton(
            master=self,
            text="Edit",
            command=self._viewmodel.edit_section_geometry,
        )
        self.button_edit_metadata = CTkButton(
            master=self,
            text="Properties",
            command=self._edit_selected_section_metadata,
        )
        self.button_remove = CTkButton(
            master=self,
            text="Remove",
            command=self._viewmodel.remove_sections,
        )

    def _place_widgets(self) -> None:
        self.treeview.pack(side=tkinter.LEFT, expand=True, fill=tkinter.BOTH)
        self._treeview_scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self._frame_tree.grid(
            row=0, column=0, columnspan=3, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_add_line.grid(row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_add_area.grid(row=1, column=1, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_edit_geometry.grid(
            row=2, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_edit_metadata.grid(
            row=2, column=1, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_remove.grid(
            row=3, column=0, columnspan=2, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _edit_selected_section_metadata(self) -> None:
        asyncio.run(self._viewmodel.edit_selected_section_metadata())

    def _set_button_state_categories(self) -> None:
        self._general_buttons: list[CTkButton] = []
        self._add_buttons = [
            self.button_add_line,
            self.button_add_area,
        ]
        self._single_item_buttons = [
            self.button_edit_geometry,
            self.button_edit_metadata,
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


class TreeviewSections(TreeviewTemplate):
    def __init__(self, viewmodel: ViewModel, **kwargs: Any) -> None:
        self._viewmodel = viewmodel
        super().__init__(**kwargs)
        self._introduce_to_viewmodel()
        self.update_items()

    def _define_columns(self) -> None:
        columns = [COLUMN_NAME]
        self["columns"] = columns
        self.column(column="#0", width=0, stretch=False)
        self.column(column=COLUMN_NAME, anchor="center", width=150, minwidth=40)
        self["displaycolumns"] = columns

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_treeview_sections(self)

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        self._viewmodel.set_selected_section_ids(ids)

    def _on_double_click(self, event: Any) -> None:
        asyncio.run(self._viewmodel.edit_selected_section_metadata())

    def update_items(self) -> None:
        self.delete(*self.get_children())
        item_ids = ColumnResources(
            sorted(
                [
                    self.__to_resource(section)
                    for section in self._viewmodel.get_all_sections()
                ]
            )
        )
        self.add_items(item_ids=item_ids)

    @staticmethod
    def __to_resource(section: Section) -> ColumnResource:
        values = {COLUMN_NAME: section.name}
        return ColumnResource(id=section.id.id, values=values)


class ListboxSections(Listbox):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # This call should come from outside later
        sections = ["North", "West", "South", "East"]
        self.show(sections=sections)

    def show(self, sections: list[str]) -> None:
        for i, section in enumerate(sections):
            self.insert(i, section)
