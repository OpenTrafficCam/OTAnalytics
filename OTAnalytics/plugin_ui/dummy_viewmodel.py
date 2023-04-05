from pathlib import Path
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import TypedDict

from plugin_ui.abstract_canvas_background import AbstractCanvasBackground

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.plugin_ui.line_section import LineSectionBuilder, LineSectionDrawer
from OTAnalytics.plugin_ui.toplevel_sections import ToplevelSections
from OTAnalytics.plugin_ui.view_model import ViewModel


class DummySections(TypedDict):
    id: str
    point0: tuple[int, int]
    point1: tuple[int, int]


DUMMY_SECTIONS: list[DummySections] = [
    {"id": "section1", "point0": (50, 50), "point1": (100, 100)},
    {"id": "section2", "point0": (200, 200), "point1": (300, 200)},
    {"id": "section3", "point0": (300, 300), "point1": (300, 400)},
]


class DummyViewModel(ViewModel):
    def __init__(self, datastore: Datastore) -> None:
        self._datastore = datastore
        self._canvas: AbstractCanvasBackground | None = None

    def load_tracks(self) -> None:
        tracks_file = askopenfilename(
            title="Load tracks file", filetypes=[("tracks file", "*.ottrk")]
        )
        print(f"Tracks file to load: {tracks_file}")
        self._datastore.load_track_file(file=Path(tracks_file))

    def load_sections(self) -> None:  # sourcery skip: avoid-builtin-shadow
        # ? Overwrite or append new sections ?
        if self._canvas is None:
            raise ValueError(
                "Gui has to tell DummyViewModel about itself before loading sections"
            )
        sections_file = askopenfilename(
            title="Load sections file", filetypes=[("sections file", "*.otflow")]
        )
        print(f"Sections file to load: {sections_file}")
        self._datastore.load_section_file(file=Path(sections_file))
        # TODO: Retrieve line_sections from model
        line_section_drawer = LineSectionDrawer(canvas=self._canvas)
        for line_section in DUMMY_SECTIONS:
            line_section_drawer.draw_section(
                id=line_section["id"],
                point0=line_section["point0"],
                point1=line_section["point1"],
            )

    def save_sections(self) -> None:
        sections_file = asksaveasfilename(
            title="Load sections file", filetypes=[("sections file", "*.otflow")]
        )
        print(f"Sections file to save: {sections_file}")

    def remove_section(self) -> None:
        # TODO: Get currently selected sections (?)
        pass

    def add_section(self) -> None:
        self._add_section_geometry()

    def _add_section_geometry(self) -> None:
        if self._canvas is None:  # or self._gui is None
            raise ValueError(
                "Canvas has to tell DummyViewModel about itself before adding a section"
            )
        # frames_to_disable = [self._gui.frame_sections, self._gui.frame_tracks]
        LineSectionBuilder(
            view_model=self,
            canvas=self._canvas,
            # frames_to_disable=frames_to_disable,
        )

    def _add_section_metadata(self) -> None:
        section_metadata = ToplevelSections(title="New section").get_metadata()
        print(f"New LineSection Metadata: {section_metadata}")

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

    def set_new_section_geometry(
        self, point0: tuple[int, int], point1: tuple[int, int]
    ) -> None:
        x0, y0 = point0
        x1, y1 = point1
        print(f"New LineSection Geometry: x0={x0}, y0={y0}, x1={x1}, y1={y1}")

    def set_canvas(self, canvas: AbstractCanvasBackground) -> None:
        self._canvas = canvas
