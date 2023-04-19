# from customtkinter import CTkFrame

from abc import ABC, abstractmethod
from typing import Optional

from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import ID, LineSection, Section, SectionId
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.plugin_ui.canvas_observer import CanvasObserver
from OTAnalytics.plugin_ui.helpers import get_widget_position
from OTAnalytics.plugin_ui.toplevel_sections import ToplevelSections
from OTAnalytics.plugin_ui.view_model import ViewModel

TEMPORARY_SECTION_ID: str = "temporary_section"
LINE_WIDTH: int = 4
LINE_COLOR: str = "lightgreen"

# TODO: If possible make this classes reusable for other canvas items
# TODO: Rename to more canvas specific names, as LineSection also has metadata


class LineSectionGeometryBuilderObserver(ABC):
    @abstractmethod
    def finish_building(
        self,
        coordinates: list[tuple[int, int]],
    ) -> None:
        """
        Receives line section start and end coordinates from LineSectionGeometryBuilder.
        """
        raise NotImplementedError


class CanvasElementPainter:
    def __init__(self, canvas: AbstractCanvas) -> None:
        self._canvas = canvas

    def draw(
        self,
        tags: list[str],
        id: str,
        start: tuple[int, int],
        end: tuple[int, int],
        line_width: int = LINE_WIDTH,
        line_color: str = LINE_COLOR,
    ) -> None:
        """Draws a line section on a canvas.

        Args:
            tag (str): Tag for groups of line_sections
            id (str): ID of the line section. Has to be unique among all line sections.
            start (tuple[int, int]): _description_
            end (tuple[int, int]): _description_
            line_width (int, optional): _description_. Defaults to LINE_WIDTH.
            line_color (str, optional): _description_. Defaults to LINE_COLOR.
        """
        tkinter_tags = (id,) + tuple(tags)
        x0, y0 = start
        x1, y1 = end
        self._canvas.create_line(
            x0, y0, x1, y1, width=line_width, fill=line_color, tags=tkinter_tags
        )


class CanvasElementUpdater:
    def __init__(self, canvas: AbstractCanvas) -> None:
        self._canvas = canvas

    def update(self, id: str, start: tuple[int, int], end: tuple[int, int]) -> None:
        """Updates the coordinates of a line_section.
        This is a faster alternative to deleting and repainting a line_section.
        Currently used, when line_section is updated very often.

        Args:
            id (str): ID of the line_section
            start (tuple[int, int]): Tuple of the sections start coordinates
            end (tuple[int, int]): Tuple of the sections end coordinates
        """
        x0, y0 = start
        x1, y1 = end
        self._canvas.coords(id, x0, y0, x1, y1)


class CanvasElementDeleter:
    def __init__(self, canvas: AbstractCanvas) -> None:
        self._canvas = canvas

    def delete(self, tag_or_id: str) -> None:
        """Deletes all elements from a canvas with a given tag or id.

        Args:
            tag (str): Tag given when creating a canvas item (e.g. "line_section")
        """
        self._canvas.delete(tag_or_id)


class LineSectionGeometryBuilder:
    def __init__(
        self,
        observer: LineSectionGeometryBuilderObserver,
        canvas: AbstractCanvas,
    ) -> None:
        self._observer = observer

        self.painter = CanvasElementPainter(canvas=canvas)
        self.updater = CanvasElementUpdater(canvas=canvas)
        self.deleter = CanvasElementDeleter(canvas=canvas)

        self._temporary_id: str = TEMPORARY_SECTION_ID
        self._start: tuple[int, int] | None = None
        self._tmp_end: tuple[int, int] | None = None
        self._end: tuple[int, int] | None = None
        self._coordinates: list[tuple[int, int]] = []

    def _set_start(self, coordinate: tuple[int, int]) -> None:
        self._start = coordinate
        self._coordinates.append(coordinate)

    def _set_tmp_end(self, coordinates: tuple[int, int]) -> None:
        if self._start is None:
            raise ValueError("self.start as to be set before listening to mouse motion")
        if self._tmp_end is None:
            self.painter.draw(
                tags=["temporary_line_section"],
                id=self._temporary_id,
                start=self._start,
                end=coordinates,
                line_color="red",
            )
        else:
            self.updater.update(
                id=self._temporary_id,
                start=self._start,
                end=coordinates,
            )
        self._tmp_end = coordinates

    def _set_end(self, coordinate: tuple[int, int]) -> None:
        self._end = coordinate
        self._coordinates.append(coordinate)
        self._finish_building()

    def _finish_building(self) -> None:
        if self._start is None or self._end is None:
            raise ValueError(
                "Both self.start and self.end have to be set to finish building"
            )
        self._observer.finish_building(self._coordinates)
        self.deleter.delete(tag_or_id="temporary_line_section")


class MissingCoordinate(Exception):
    pass


class LineSectionBuilder(LineSectionGeometryBuilderObserver, CanvasObserver):
    def __init__(
        self,
        viewmodel: ViewModel,
        canvas: AbstractCanvas,
        section: Optional[Section] = None,
    ) -> None:
        self._viewmodel = viewmodel
        self._canvas = canvas
        self.attach_to(self._canvas.event_handler)
        self.geometry_builder = LineSectionGeometryBuilder(
            observer=self, canvas=self._canvas
        )
        self._name: Optional[str] = None
        self._coordinates: list[tuple[int, int]] = []
        self._metadata: dict[str, str] = {}
        self._initialise_with(section)

    def _initialise_with(self, section: Optional[Section]) -> None:
        if template := section:
            self._coordinates = [
                (int(coordinate.x), int(coordinate.y))
                for coordinate in template.get_coordinates()
            ]
            self._name = template.id.id
            self._metadata = template.to_dict()

    def update(self, coordinate: tuple[int, int], event_type: str) -> None:
        """Receives and reacts to updates issued by the canvas event handler

        Args:
            coordinates (tuple[int, int]): Coordinates clicked on canvas
            event_type (str): Event type of canvas click
        """
        if self.geometry_builder._start is None and event_type == "left_mousebutton_up":
            self.geometry_builder._set_start(coordinate)
        elif self.geometry_builder._start is not None and event_type == "mouse_motion":
            self.geometry_builder._set_tmp_end(coordinate)
        elif (
            self.geometry_builder._start is not None
            and event_type == "left_mousebutton_up"
        ):
            self.geometry_builder._set_end(coordinate)
            self.detach_from(self._canvas.event_handler)

    def finish_building(
        self,
        coordinates: list[tuple[int, int]],
    ) -> None:
        """Sets a line section geomatry from the GeometryBuilder and triggers
        further tasks.

        Args:
            start (tuple[int, int]): Tuple of the sections start coordinates
            end (tuple[int, int]): Tuple of the sections end coordinates
        """
        self._coordinates = coordinates
        if ID not in self._metadata:
            self._get_metadata()
        self._create_section()

    def _get_metadata(self) -> None:
        toplevel_position = get_widget_position(widget=self._canvas)
        self._metadata = ToplevelSections(
            title="New section", initial_position=toplevel_position
        ).get_metadata()

    def _create_section(self) -> None:
        if self._start() is None or self._end() is None:
            raise ValueError("Start and end of line_section are not defined")
        if self._metadata == {}:
            raise ValueError("Metadata of line_section are not defined")
        name = self._metadata[ID]
        line_section = LineSection(
            id=SectionId(name),
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(0, 0)
            },
            plugin_data={},
            start=Coordinate(self._start()[0], self._start()[1]),
            end=Coordinate(self._end()[0], self._end()[1]),
        )
        self._viewmodel.set_new_section(line_section)

    def _start(self) -> tuple[int, int]:
        if len(self._coordinates) > 0:
            return self._coordinates[0]
        raise MissingCoordinate("Start coordinate missing")

    def _end(self) -> tuple[int, int]:
        if len(self._coordinates) > 1:
            return self._coordinates[-1]
        raise MissingCoordinate("End coordinate missing")
