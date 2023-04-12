import copy
import uuid
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import TypedDict, cast

from plugin_ui.abstract_canvas_background import AbstractCanvasBackground

from OTAnalytics.application.datastore import Datastore
from OTAnalytics.plugin_ui.abstract_treeview import AbstractTreeviewSections
from OTAnalytics.plugin_ui.helpers import get_widget_position
from OTAnalytics.plugin_ui.line_section import (
    LineSectionBuilder,
    LineSectionGeometryBuilder,
    LineSectionGeometryBuilderObserver,
    LineSectionGeometryDeleter,
    LineSectionGeometryPainter,
)
from OTAnalytics.plugin_ui.messagebox import InfoBox
from OTAnalytics.plugin_ui.toplevel_sections import ToplevelSections
from OTAnalytics.plugin_ui.view_model import ViewModel


# TODO: @briemla delete code for dummy sections
class DummySection(TypedDict):
    id: str
    name: str
    start: tuple[int, int]
    end: tuple[int, int]


DUMMY_SECTIONS: list[DummySection] = [
    {"id": "section1", "name": "West", "start": (50, 50), "end": (100, 100)},
    {"id": "section2", "name": "East", "start": (200, 200), "end": (300, 200)},
    {"id": "section3", "name": "North", "start": (300, 300), "end": (300, 400)},
]


class MissingInjectedInstanceError(Exception):
    """Raises when no instance of an object was injected before referencing it"""

    def __init__(self, injected_object: str):
        message = (
            f"An instance of {injected_object} has to be injected before referencing it"
        )
        super().__init__(message)


class DummyViewModel(ViewModel, LineSectionGeometryBuilderObserver):
    def __init__(self, datastore: Datastore) -> None:
        self._datastore = datastore
        self._canvas: AbstractCanvasBackground | None = None
        self._treeview_sections: AbstractTreeviewSections | None
        self._new_section: dict = {}
        self._sections: list[DummySection] = []
        self._selected_section_id: str | None = None

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
        if not self._sections:
            if self._treeview_sections is None:
                raise MissingInjectedInstanceError(injected_object="treeview_sections")
            position = get_widget_position(widget=self._treeview_sections)
            InfoBox(
                message="No sections to save, please add new sections first",
                initial_position=position,
            )
            return
        sections_file = asksaveasfilename(
            title="Save sections file as", filetypes=[("sections file", "*.otflow")]
        )
        print(f"Sections file to save: {sections_file}")

    def add_section(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(injected_object="canvas")
        LineSectionBuilder(viewmodel=self, canvas=self._canvas)

    def set_new_section(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
        metadata: dict[str, str],
    ) -> None:
        # TODO: @briemla delete block and connect to model
        name = metadata["name"]
        new_section = DummySection(
            id=str(uuid.uuid1()),
            name=name,
            start=start,
            end=end,
        )
        self._sections.append(new_section)
        print(f"New line_section created with name={name}, start={start} and end={end}")

        self._refresh_sections_on_gui()

    def edit_section_geometry(self) -> None:
        self._selected_section_id = self._get_selected_section_id()
        if self._selected_section_id is None:
            return
        if self._canvas is None:
            raise MissingInjectedInstanceError(injected_object="canvas")
        LineSectionGeometryDeleter(canvas=self._canvas).delete_sections(
            tag_or_id=self._selected_section_id
        )
        LineSectionGeometryBuilder(observer=self, canvas=self._canvas)

    def set_section_geometry(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> None:
        # TODO: @briemla delete block and connect to model
        for section in self._sections:
            if section["id"] == self._selected_section_id:
                section["start"] = start
                section["end"] = end
        print(f"Updated line_section geometry with start={start} and end={end}")

        self._refresh_sections_on_gui()

    def edit_section_metadata(self) -> None:
        selected_section_id = self._get_selected_section_id()
        if selected_section_id is None:
            return
        current_metadata = self._get_section_metadata(selected_section_id)
        if self._canvas is None:
            raise MissingInjectedInstanceError(injected_object="canvas")
        position = get_widget_position(widget=self._canvas)
        updated_section_metadata = ToplevelSections(
            title="Edit section",
            initial_position=position,
            input_values=current_metadata,
        ).get_metadata()
        self._set_section_metadata(
            id=selected_section_id, metadata=updated_section_metadata
        )
        self._refresh_sections_on_gui()
        print(f"Updated line_section Metadata: {updated_section_metadata}")

    def _get_section_metadata(self, id: str) -> dict:
        # TODO: @briemla delete block and connect to model
        for section in self._sections:
            if section["id"] == id:
                current_metadata = {k: v for k, v in section.items() if k in ["name"]}
                break
        return current_metadata

    def _set_section_metadata(self, id: str, metadata: dict) -> None:
        # TODO: @briemla delete block and connect to model
        new_metadata = metadata
        for index, section in enumerate(self._sections):
            if section["id"] == id:
                new_data = dict(section) | new_metadata
                updated_section = cast(DummySection, new_data)
                self._sections[index] = updated_section
                break

    def remove_section(self) -> None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(injected_object="treeview_sections")
        selected_section_id = self._treeview_sections.focus()
        if not selected_section_id:
            position = get_widget_position(widget=self._treeview_sections)
            InfoBox(
                message="Please select a section to remove", initial_position=position
            )
            return
        for section in self._sections:
            if section["id"] == selected_section_id:
                self._sections.remove(section)
                print(f"This section was removed: {section}")
        self._refresh_sections_on_gui()

    def _get_selected_section_id(self) -> str | None:
        if self._treeview_sections is None:
            raise MissingInjectedInstanceError(injected_object="treeview_sections")
        selected_section_id = self._treeview_sections.get_selected_section()
        position = get_widget_position(widget=self._treeview_sections)
        if not selected_section_id:
            InfoBox(
                message="Please select a section to edit", initial_position=position
            )
            return None
        return selected_section_id

    def _refresh_sections_on_gui(self) -> None:
        self._remove_all_sections_from_canvas()
        self._remove_all_sections_from_treeview()
        self._draw_all_sections_on_canvas()
        self._list_all_sections_in_treeview()

    def _draw_all_sections_on_canvas(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(injected_object="canvas")
        line_section_drawer = LineSectionGeometryPainter(canvas=self._canvas)
        for line_section in self._sections:
            line_section_drawer.draw_section(
                tags=["line_section"],
                id=line_section["id"],
                start=line_section["start"],
                end=line_section["end"],
            )

    def _remove_all_sections_from_canvas(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(injected_object="canvas")
        LineSectionGeometryDeleter(canvas=self._canvas).delete_sections(
            tag_or_id="line_section"
        )

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
