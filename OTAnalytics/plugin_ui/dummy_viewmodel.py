import uuid
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import TypedDict

from plugin_ui.abstract_canvas_background import AbstractCanvasBackground

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.plugin_ui.abstract_treeview import AbstractTreeviewSections
from OTAnalytics.plugin_ui.line_section import LineSectionBuilder, LineSectionDrawer
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
        self._sections = DUMMY_SECTIONS
        self._draw_sections_on_canvas()
        self._list_sections_in_treeview()

    def save_sections(self) -> None:
        sections_file = asksaveasfilename(
            title="Load sections file", filetypes=[("sections file", "*.otflow")]
        )
        print(f"Sections file to save: {sections_file}")

    def remove_section(self) -> None:
        # TODO: Get currently selected sections (?)
        pass

    def add_section(self) -> None:
        self._new_section["id"] = uuid.uuid1()
        self._add_section_geometry()

    def edit_section_geometry(self) -> None:
        # TODO: Make sure only one section is selected
        # TODO: Get currently selected section
        # TODO: Enter drawing mode (there, old section is deleted, first)
        # TODO: Yield updated geometry
        print("Update geometry of selected section")

    def edit_section_metadata(self) -> None:
        # TODO: Make sure only one section is selected
        # TODO: Get currently selected section
        # TODO: Retrieve sections metadata via ID from selection in Treeview
        INPUT_VALUES: dict = {"name": "Existing Section"}
        updated_section_metadata = ToplevelSections(
            title="Edit section", input_values=INPUT_VALUES
        ).get_metadata()
        print(f"Uodated LineSection Metadata: {updated_section_metadata}")

    def _add_section_geometry(self) -> None:
        if self._canvas is None:  # or self._gui is None
            raise ValueError(
                "Canvas has to tell DummyViewModel about itself before adding a section"
            )
        # frames_to_disable = [self._gui.frame_sections, self._gui.frame_tracks]
        # BUG: Adding 2+ sections doesnt work
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
        section_metadata = ToplevelSections(title="New section").get_metadata()
        self._new_section["name"] = section_metadata["name"]
        self._finish_adding_section()
        # TODO: @briemla provide for model
        print(f"New LineSection Metadata: {section_metadata}")

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
        self._draw_sections_on_canvas()
        self._list_sections_in_treeview()
        # TODO: @briemla provide for model
        # Teardown
        self._new_section = {}

    def _draw_sections_on_canvas(self) -> None:
        if self._canvas is None:
            raise ValueError(
                "Gui has to tell DummyViewModel about itself before drawing sections"
            )
        line_section_drawer = LineSectionDrawer(canvas=self._canvas)
        for line_section in self._sections:
            line_section_drawer.draw_section(
                id=line_section["id"],
                point0=line_section["point0"],
                point1=line_section["point1"],
            )

    def _list_sections_in_treeview(self) -> None:
        if self._treeview_sections is None:
            raise ValueError(
                "Treeview has to tell DummyViewModel about itself before listing "
                + "sections"
            )
        self._treeview_sections.delete(*self._treeview_sections.get_children())
        for line_section in self._sections:
            self._treeview_sections.add_section(
                id=line_section["id"], name=line_section["name"]
            )
