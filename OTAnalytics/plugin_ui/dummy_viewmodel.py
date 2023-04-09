import copy
import uuid
from tkinter import Widget
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import TypedDict, cast

from plugin_ui.abstract_canvas_background import AbstractCanvasBackground

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.plugin_ui.abstract_treeview import AbstractTreeviewSections
from OTAnalytics.plugin_ui.line_section import (
    LineSectionBuilder,
    LineSectionDeleter,
    LineSectionDrawer,
)
from OTAnalytics.plugin_ui.messagebox import InfoBox
from OTAnalytics.plugin_ui.toplevel_sections import ToplevelSections
from OTAnalytics.plugin_ui.view_model import ViewModel


class DummySection(TypedDict):
    id: str
    name: str
    point0: tuple[int, int]
    point1: tuple[int, int]


DUMMY_SECTIONS: list[DummySection] = [
    {"id": "section1", "name": "West", "point0": (50, 50), "point1": (100, 100)},
    {"id": "section2", "name": "East", "point0": (200, 200), "point1": (300, 200)},
    {"id": "section3", "name": "North", "point0": (300, 300), "point1": (300, 400)},
]


class MissingInjectedInstanceError(Exception):
    """Raises when no instance of an object was injected before referencing it"""

    def __init__(self, injected_object: str):
        message = (
            f"An instance of {injected_object} has to be injected before referencing it"
        )
        super().__init__(message)


class DummyViewModel(ViewModel):
    def __init__(self, datastore: Datastore) -> None:
        self._datastore = datastore
        self._canvas: AbstractCanvasBackground | None = None
        self._treeview_sections: AbstractTreeviewSections | None
        self._new_section: dict = {}
        self._sections: list[DummySection] = []

    def set_canvas(self, canvas: AbstractCanvasBackground) -> None:
        self._canvas = canvas

    def set_treeview_sections(self, treeview: AbstractTreeviewSections) -> None:
        self._treeview_sections = treeview

    def load_tracks(self) -> None:
        tracks_file = askopenfilename(
            title="Load tracks file", filetypes=[("tracks file", "*.ottrk")]
        )
        print(f"Tracks file to load: {tracks_file}")
        # TODO: @briemla retrieve, store and show tracks via model

    def load_sections(self) -> None:  # sourcery skip: avoid-builtin-shadow
        # INFO: Current behavior: Overwrites existing sections
        sections_file = askopenfilename(
            title="Load sections file", filetypes=[("otflow file", "*.otflow")]
        )
        if not sections_file:
            return
        print(f"Sections file to load: {sections_file}")
        # TODO: @briemla retrieve line_sections from file via model
        self._sections = copy.deepcopy(DUMMY_SECTIONS)
        self._refresh_sections_on_gui()

    def save_sections(self) -> None:
        sections_file = asksaveasfilename(
            title="Load sections file", filetypes=[("sections file", "*.otflow")]
        )
        print(f"Sections file to save: {sections_file}")

    def remove_section(self) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(injected_object="treeview_sections")
        selected_section_id = self._treeview_sections.focus()
        if not selected_section_id:
            position = self._get_absolute_position(widget=self._treeview_sections)
            InfoBox(
                message="Please select a section to remove", initial_position=position
            )
            return
        for section in self._sections:
            if section["id"] == selected_section_id:
                self._sections.remove(section)
                print(f"This section was removed: {section}")
        self._refresh_sections_on_gui()

    def add_section(self) -> None:
        self._new_section["id"] = str(uuid.uuid1())
        self._add_section_geometry()

    def edit_section_geometry(self) -> None:
        # TODO: Get currently selected section
        # TODO: Enter drawing mode (there, old section is deleted, first)
        # TODO: Yield updated geometry
        print("Update geometry of selected section")

    def edit_section_metadata(self) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(injected_object="treeview_sections")
        selected_section_id = self._treeview_sections.get_selected_section()
        position = self._get_absolute_position(widget=self._treeview_sections)
        if not selected_section_id:
            InfoBox(
                message="Please select a section to edit", initial_position=position
            )
            return
        current_metadata = self._get_section_metadata(selected_section_id)
        if self._canvas is None:  # or self._gui is None
            raise MissingInjectedInstanceError(injected_object="canvas")
        position = self._get_absolute_position(widget=self._canvas)
        updated_section_metadata = ToplevelSections(
            title="Edit section",
            initial_position=position,
            input_values=current_metadata,
        ).get_metadata()
        self._set_section_metadata(
            id=selected_section_id, metadata=updated_section_metadata
        )
        print(f"Updated LineSection Metadata: {updated_section_metadata}")

    def _get_section_metadata(self, id: str) -> dict:
        for section in self._sections:
            if section["id"] == id:
                current_metadata = {k: v for k, v in section.items() if k in ["name"]}
                break
        return current_metadata

    def _set_section_metadata(self, id: str, metadata: dict) -> None:
        new_metadata = metadata
        for index, section in enumerate(self._sections):
            if section["id"] == id:
                new_data = dict(section) | new_metadata
                # if set(new_data.keys()) != set(section.__annotations__.keys()):
                #     raise ValueError("new_data does not have all required keys")
                updated_section = cast(DummySection, new_data)
                self._sections[index] = updated_section
                break

    def _add_section_geometry(self) -> None:
        if self._canvas is None:  # or self._gui is None
            raise MissingInjectedInstanceError(injected_object="canvas")
        # frames_to_disable = [self._gui.frame_sections, self._gui.frame_tracks]
        LineSectionBuilder(
            view_model=self,
            canvas=self._canvas,
            # frames_to_disable=frames_to_disable,
        )

    def set_new_section_geometry(
        self, point0: tuple[int, int], point1: tuple[int, int]
    ) -> None:
        self._new_section["point0"] = point0
        self._new_section["point1"] = point1
        self._add_section_metadata()

    def _add_section_metadata(self) -> None:
        if self._canvas is None:  # or self._gui is None
            raise MissingInjectedInstanceError(injected_object="canvas")
        position = self._get_absolute_position(widget=self._canvas)
        section_metadata = ToplevelSections(
            title="New section", initial_position=position
        ).get_metadata()
        self._new_section["name"] = section_metadata["name"]
        self._finish_adding_section()
        # TODO: @briemla provide for model
        print(f"New LineSection Metadata: {section_metadata}")

    def _get_absolute_position(self, widget: Widget) -> tuple[int, int]:
        x = widget.winfo_rootx()
        y = widget.winfo_rooty()
        return x, y

    def _finish_adding_section(self) -> None:
        for key in ["id", "name", "point0", "point1"]:
            if key not in self._new_section:
                raise ValueError(
                    f"{key} has to be specified before finish adding the section"
                )
        new_section = DummySection(
            id=self._new_section["id"],
            name=self._new_section["name"],
            point0=self._new_section["point0"],
            point1=self._new_section["point1"],
        )
        self._sections.append(new_section)
        self._refresh_sections_on_gui()
        # TODO: @briemla provide for model
        # Teardown
        self._new_section = {}

    def _refresh_sections_on_gui(self) -> None:
        self._remove_all_sections_from_canvas()
        self._remove_all_sections_from_treeview()
        self._draw_all_sections_on_canvas()
        self._list_all_sections_in_treeview()

    def _draw_all_sections_on_canvas(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(injected_object="canvas")
        line_section_drawer = LineSectionDrawer(canvas=self._canvas)
        for line_section in self._sections:
            line_section_drawer.draw_section(
                tag="line_section",
                id=line_section["id"],
                point0=line_section["point0"],
                point1=line_section["point1"],
            )

    def _remove_all_sections_from_canvas(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(injected_object="canvas")
        LineSectionDeleter(canvas=self._canvas).delete_sections(tag="line_section")

    def _list_all_sections_in_treeview(self) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(injected_object="treeview_sections")
        for line_section in self._sections:
            self._treeview_sections.add_section(
                id=line_section["id"], name=line_section["name"]
            )

    def _remove_all_sections_from_treeview(self) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(injected_object="treeview_sections")
        self._treeview_sections.delete(*self._treeview_sections.get_children())
