from pathlib import Path
from tkinter.filedialog import askopenfilename, asksaveasfilename
from typing import Iterable, TypedDict, cast

from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.datastore import NoSectionsToSave
from OTAnalytics.domain import geometry
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import END, ID, START, LineSection, SectionId
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_ui.abstract_canvas import AbstractCanvas
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

LINE_SECTION: str = "line_section"


# TODO: @briemla delete code for dummy sections
class DummySection(TypedDict):
    id: str
    name: str
    start: tuple[int, int]
    end: tuple[int, int]


class MissingInjectedInstanceError(Exception):
    """Raises when no instance of an object was injected before referencing it"""

    def __init__(self, injected_object: str):
        message = (
            f"An instance of {injected_object} has to be injected before referencing it"
        )
        super().__init__(message)


class DummyViewModel(ViewModel, LineSectionGeometryBuilderObserver):
    def __init__(self, application: OTAnalyticsApplication) -> None:
        self._application = application
        self._canvas: AbstractCanvas | None = None
        self._treeview_sections: AbstractTreeviewSections | None
        self._new_section: dict = {}
        self._sections: list[DummySection] = []
        self._selected_section_id: str | None = None

    def set_canvas(self, canvas: AbstractCanvas) -> None:
        self._canvas = canvas

    def set_treeview_sections(self, treeview: AbstractTreeviewSections) -> None:
        self._treeview_sections = treeview

    def set_selected_section_id(self, id: str) -> None:
        self._selected_section_id = id
        print(f"New line section selected in treeview: id={id}")

    def load_tracks(self) -> None:
        track_file = askopenfilename(
            title="Load tracks file", filetypes=[("tracks file", "*.ottrk")]
        )
        if not track_file:
            return
        print(f"Tracks file to load: {track_file}")
        self._application.add_tracks_of_file(track_file=Path(track_file))

    def load_sections(self) -> None:  # sourcery skip: avoid-builtin-shadow
        # INFO: Current behavior: Overwrites existing sections
        sections_file = askopenfilename(
            title="Load sections file", filetypes=[("otflow file", "*.otflow")]
        )
        if not sections_file:
            return
        print(f"Sections file to load: {sections_file}")
        self._application.add_sections_of_file(sections_file=Path(sections_file))
        self.refresh_sections_on_gui()

    def save_sections(self) -> None:
        sections_file = asksaveasfilename(
            title="Save sections file as", filetypes=[("sections file", "*.otflow")]
        )
        if not sections_file:
            return
        print(f"Sections file to save: {sections_file}")
        try:
            self._application.save_sections(Path(sections_file))
        except NoSectionsToSave:
            if self._treeview_sections is None:
                raise MissingInjectedInstanceError(injected_object="treeview_sections")
            position = get_widget_position(widget=self._treeview_sections)
            InfoBox(
                message="No sections to save, please add new sections first",
                initial_position=position,
            )
            return

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
        name = metadata["name"]
        line_section = LineSection(
            id=SectionId(name),
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            start=Coordinate(start[0], start[1]),
            end=Coordinate(end[0], end[1]),
        )
        self._application.add_section(line_section)
        print(f"New line_section created with name={name}, start={start} and end={end}")

        self.refresh_sections_on_gui()

    def edit_section_geometry(self) -> None:
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

        self.refresh_sections_on_gui()

    def edit_section_metadata(self) -> None:
        if self._selected_section_id is None:
            if self._treeview_sections is None:
                raise MissingInjectedInstanceError(injected_object="treeview_sections")
            position = get_widget_position(self._treeview_sections)
            InfoBox(
                message="Please select a section to edit", initial_position=position
            )
            return
        current_metadata = self._get_section_metadata(self._selected_section_id)
        if self._canvas is None:
            raise MissingInjectedInstanceError(injected_object="canvas")
        position = get_widget_position(widget=self._canvas)
        updated_section_metadata = ToplevelSections(
            title="Edit section",
            initial_position=position,
            input_values=current_metadata,
        ).get_metadata()
        self._set_section_metadata(
            id=self._selected_section_id, metadata=updated_section_metadata
        )
        self.refresh_sections_on_gui()
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
        if not self._selected_section_id:
            position = get_widget_position(widget=self._treeview_sections)
            InfoBox(
                message="Please select a section to remove", initial_position=position
            )
            return
        for section in self._sections:
            if section["id"] == self._selected_section_id:
                self._sections.remove(section)
                print(f"This section was removed: {section}")
        self.refresh_sections_on_gui()

    def refresh_sections_on_gui(self) -> None:
        self._remove_all_sections_from_canvas()
        self._draw_all_sections_on_canvas()

    def _draw_all_sections_on_canvas(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(injected_object="canvas")
        line_section_drawer = LineSectionGeometryPainter(canvas=self._canvas)
        for line_section in self._get_sections():
            line_section_drawer.draw_section(
                tags=[LINE_SECTION],
                id=line_section[ID],
                start=line_section[START],
                end=line_section[END],
            )

    def _get_sections(self) -> Iterable[dict]:
        return map(
            lambda section: self._transform_coordinates(section),
            map(
                lambda section: section.to_dict(),
                self._application.get_all_sections(),
            ),
        )

    def _transform_coordinates(self, section: dict) -> dict:
        section[START] = self._to_coordinate_tuple(section[START])
        section[END] = self._to_coordinate_tuple(section[END])
        return section

    def _to_coordinate_tuple(self, coordinate: dict) -> tuple[int, int]:
        return (coordinate[geometry.X], coordinate[geometry.Y])

    def _remove_all_sections_from_canvas(self) -> None:
        if self._canvas is None:
            raise MissingInjectedInstanceError(injected_object="canvas")
        LineSectionGeometryDeleter(canvas=self._canvas).delete_sections(
            tag_or_id=LINE_SECTION
        )
