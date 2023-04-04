from pathlib import Path
from tkinter import Listbox
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.ttk import Treeview
from typing import Any

from customtkinter import CTkButton, CTkFrame, CTkLabel

from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.domain.section import SectionId, SectionListObserver
from OTAnalytics.plugin_ui.constants import PADX, PADY, STICKY
from OTAnalytics.plugin_ui.toplevel_sections import ToplevelSections


class FrameSections(CTkFrame):
    def __init__(
        self,
        application: OTAnalyticsApplication,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self._application = application
        self._get_widgets(self._application)
        self._place_widgets()

    def _get_widgets(self, application: OTAnalyticsApplication) -> None:
        self.label = CTkLabel(master=self, text="Sections")
        self.listbox_sections = TreeviewSections(application, master=self)
        self.button_load_sections = CTkButton(
            master=self, text="Load", command=self._load_sections_in_file
        )
        self.button_save_sections = ButtonSaveSections(master=self, text="Save")
        self.button_new_section = ButtonNewSection(master=self, text="New")
        self.button_delete_selected_sections = ButtonDeleteSelectedSections(
            master=self, text="Remove"
        )
        self.button_edit_geometry_selected_section = (
            ButtonUpdateSelectedSectionGeometry(master=self, text="Edit geometry")
        )
        self.button_edit_metadata_selected_section = (
            ButtonUpdateSelectedSectionMetadata(master=self, text="Edit metadata")
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
        self.button_edit_geometry_selected_section.grid(
            row=5, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_edit_metadata_selected_section.grid(
            row=6, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )
        self.button_delete_selected_sections.grid(
            row=7, column=0, padx=PADX, pady=PADY, sticky=STICKY
        )

    def _load_sections_in_file(self) -> None:
        sections_file = askopenfilename(
            title="Load sections file", filetypes=[("sections file", "*.otflow")]
        )
        print(f"Sections file to load: {sections_file}")
        self._application.add_sections_of_file(Path(sections_file))


class TreeviewSections(Treeview, SectionListObserver):
    def __init__(self, application: OTAnalyticsApplication, **kwargs: Any) -> None:
        super().__init__(show="tree", **kwargs)
        self.application = application
        self.application.register_sections_observer(self)
        self.bind("<ButtonRelease-3>", self._deselect_sections)
        self._define_columns()
        # This call should come from outside later
        self._update_sections()

    def _define_columns(self) -> None:
        self["columns"] = "Section"
        self.column(column="#0", width=0)
        self.column(column="Section", anchor="center", width=80, minwidth=40)
        self["displaycolumns"] = "Section"

    def notify_sections(self, sections: list[SectionId]) -> None:
        self._update_sections()

    def _update_sections(self) -> None:
        self.delete(*self.get_children())
        sections = [section.id for section in self.application.get_all_sections()]
        self.add_sections(sections=sections)

    def add_sections(self, sections: list[SectionId]) -> None:
        for section in sections:
            self.insert(
                parent="", index="end", iid=section.id, text="", values=[section.id]
            )

    def _deselect_sections(self, event: Any) -> None:
        for item in self.selection():
            self.selection_remove(item)


class ListboxSections(Listbox):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        # This call should come from outside later
        sections = ["North", "West", "South", "East"]
        self.show(sections=sections)

    def show(self, sections: list[str]) -> None:
        for i, section in enumerate(sections):
            self.insert(i, section)


class ButtonSaveSections(CTkButton):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.bind("<ButtonRelease-1>", self.on_click)

    def on_click(self, events: Any) -> None:
        self.sections_file = asksaveasfilename(
            title="Load sections file", filetypes=[("sections file", "*.otflow")]
        )
        print(f"Sections file to save: {self.sections_file}")


class ButtonNewSection(CTkButton):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.toplevel_sections: ToplevelSections | None = None

        self.bind("<ButtonRelease-1>", self.on_click)

        self.toplevel_sections = None

    def on_click(self, events: Any) -> None:
        # TODO: Enter drawing mode
        self.get_metadata()
        # TODO: Yield geometry and metadata
        print(
            "Add new section with geometry = <TODO> and"
            + f"metadata = {self.section_metadata}"
        )

    def get_metadata(self) -> None:
        if self.toplevel_sections is None or not self.toplevel_sections.winfo_exists():
            self.toplevel_sections = ToplevelSections(title="New section")
        else:
            self.toplevel_sections.focus()
        self.section_metadata = self.toplevel_sections.show()


class ButtonUpdateSelectedSectionGeometry(CTkButton):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.bind("<ButtonRelease-1>", self.on_click)

    def on_click(self, events: Any) -> None:
        # TODO: Make sure only one section is selected
        # TODO: Get currently selected section
        # TODO: Enter drawing mode (there, old section is deleted, first)
        # TODO: Yield updated geometry
        print("Update geometry of selected section")


class ButtonUpdateSelectedSectionMetadata(CTkButton):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.toplevel_sections: ToplevelSections | None = None

        self.bind("<ButtonRelease-1>", self.on_click)

        self.toplevel_sections = None

    def on_click(self, events: Any) -> None:
        # TODO: Make sure only one section is selected
        # TODO: Get currently selected section
        self.get_metadata()
        # TODO: Yield updated metadata
        print(f"Update selected section with metadata={self.section_metadata}")

    def get_metadata(self) -> None:
        # TODO: Retrieve sections metadata via ID from selection in Treeview
        INPUT_VALUES: dict = {"name": "Existing Section"}
        if self.toplevel_sections is None or not self.toplevel_sections.winfo_exists():
            self.toplevel_sections = ToplevelSections(
                title="New section", input_values=INPUT_VALUES
            )
        else:
            self.toplevel_sections.focus()
        self.section_metadata = self.toplevel_sections.show()


class ButtonDeleteSelectedSections(CTkButton):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.bind("<ButtonRelease-1>", self.on_click)

    def on_click(self, events: Any) -> None:
        # TODO: Get currently selected sections (?)
        print("Delete selected sections")
