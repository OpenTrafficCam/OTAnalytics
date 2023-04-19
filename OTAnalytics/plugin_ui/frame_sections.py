from pathlib import Path
from tkinter import Listbox
from tkinter.filedialog import askopenfilename
from typing import Any, Optional

from customtkinter import CTkButton, CTkFrame, CTkLabel

from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.domain.section import SectionId, SectionListObserver
from OTAnalytics.plugin_ui.abstract_treeview import AbstractTreeviewSections
from OTAnalytics.plugin_ui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.view_model import ViewModel


class FrameSections(CTkFrame):
    def __init__(
        self,
        viewmodel: ViewModel,
        application: OTAnalyticsApplication,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._viewmodel = viewmodel
        self._application = application
        self._get_widgets(self._application)
        self._place_widgets()

    def _get_widgets(self, application: OTAnalyticsApplication) -> None:
        self.label = CTkLabel(master=self, text="Sections")
        self.listbox_sections = TreeviewSections(
            viewmodel=self._viewmodel, application=application, master=self
        )
        self.button_load_sections = CTkButton(
            master=self, text="Load", command=self._viewmodel.load_sections
        )
        self.button_save_sections = CTkButton(
            master=self, text="Save", command=self._viewmodel.save_sections
        )
        self.button_new_section = CTkButton(
            master=self, text="New", command=self._viewmodel.add_section
        )
        self.button_delete_section = CTkButton(
            master=self, text="Remove", command=self._viewmodel.remove_section
        )
        self.button_edit_section_geometry = CTkButton(
            master=self,
            text="Edit geometry",
            command=self._viewmodel.edit_section_geometry,
        )
        self.button_edit_section_metadata = CTkButton(
            master=self,
            text="Edit metadata",
            command=self._viewmodel.edit_section_metadata,
        )

    def _place_widgets(self) -> None:
        self.label.grid(row=0, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_load_sections.grid(
            row=1, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_save_sections.grid(
            row=2, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.listbox_sections.grid(row=3, column=0, padx=PADX, pady=PADY, sticky=STICKY)
        self.button_new_section.grid(
            row=4, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_edit_section_geometry.grid(
            row=5, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_edit_section_metadata.grid(
            row=6, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_delete_section.grid(
            row=7, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _load_sections_in_file(self) -> None:
        sections_file = askopenfilename(
            title="Load sections file", filetypes=[("sections file", "*.otflow")]
        )
        print(f"Sections file to load: {sections_file}")
        self._application.add_sections_of_file(Path(sections_file))


class TreeviewSections(AbstractTreeviewSections, SectionListObserver):
    def __init__(
        self, viewmodel: ViewModel, application: OTAnalyticsApplication, **kwargs: Any
    ) -> None:
        super().__init__(show="tree", selectmode="browse", **kwargs)
        self._viewmodel = viewmodel
        self.application = application
        self.application.register_sections_observer(self)
        self.bind("<ButtonRelease-2>", self._deselect_sections)
        self.bind("<<TreeviewSelect>>", self.notify_viewmodel)
        self._define_columns()
        self.introduce_to_viewmodel()
        self._update_sections()
        self.application.section_state.selected_section.register(self._update_selection)

    def introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_treeview_sections(self)

    def _define_columns(self) -> None:
        self["columns"] = "Section"
        self.column(column="#0", width=0)
        self.column(column="Section", anchor="center", width=80, minwidth=40)
        self["displaycolumns"] = "Section"

    def notify_sections(self, sections: list[SectionId]) -> None:
        self._update_sections()

    def add_section(self, id: str, name: str) -> None:
        self.insert(parent="", index="end", iid=id, text="", values=[name])

    def _update_sections(self) -> None:
        self.delete(*self.get_children())
        sections = [section.id for section in self.application.get_all_sections()]
        self.add_sections(sections=sections)

    def add_sections(self, sections: list[SectionId]) -> None:
        for section in sections:
            self.insert(
                parent="", index="end", iid=section.id, text="", values=[section.id]
            )

    def _update_selection(self, section_id: Optional[SectionId]) -> None:
        if section_id:
            self.selection_set(section_id.id)
        else:
            self._deselect_all()

    def _deselect_sections(self, event: Any) -> None:
        self._deselect_all()

    def _deselect_all(self) -> None:
        for item in self.selection():
            self.selection_remove(item)

    def notify_viewmodel(self, event: Any) -> None:
        selection = self.selection()
        if len(selection) == 0:
            line_section_id = None
        elif len(selection) == 1:
            line_section_id = SectionId(selection[0])
        else:
            raise ValueError("Only one item in TreeviewSections shall be selected")
        self.application.section_state.selected_section.set(line_section_id)


class ListboxSections(Listbox):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # This call should come from outside later
        sections = ["North", "West", "South", "East"]
        self.show(sections=sections)

    def show(self, sections: list[str]) -> None:
        for i, section in enumerate(sections):
            self.insert(i, section)
