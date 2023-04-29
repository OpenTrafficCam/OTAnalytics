# from customtkinter import CTkFrame

from abc import ABC, abstractmethod
from typing import Callable, Optional

from OTAnalytics.adapter_ui.abstract_canvas import AbstractCanvas
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain.geometry import Coordinate, RelativeOffsetCoordinate
from OTAnalytics.domain.section import (
    ID,
    RELATIVE_OFFSET_COORDINATES,
    LineSection,
    Section,
    SectionId,
)
from OTAnalytics.domain.types import EventType
from OTAnalytics.plugin_ui.customtkinter_gui.canvas_observer import CanvasObserver
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import get_widget_position
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_sections import ToplevelSections

TEMPORARY_SECTION_ID: str = "temporary_section"

LINE_COLOR: str = "outline"  # Has to be set to "fill" for CTkCanvas.create_line
"""Specifies the line colour.
The given value may be any valid Tk colour.
If the value is an empty string, then the line will be transparent.
The default values are as follows:
    MacOS & Windows: platform default foreground colour
    Unix: black
"""

LINE_WIDTH: str = "width"
"""Specifies the width of the line or outline.
Only applied in combination wit LINE_COLOR.
The default value is 1."""

LINE_DASH: str = "dash"
"""Specifies dash patterns of the line (correspondingly).
The value may be any valid Tk dash style. The default value is a solid line."""

LINE_DASH_OFFSET: str = "dashoffset"
"""The starting offset in pixels into the pattern provided by the dash option.
Is ignored if there is no dash pattern.
The offset may have any of the forms described in the coordinates section below.
The default value is 0."""

LINE_CAPS: str = "capstyle"
"""Specifies the ways in which caps are to be drawn at the endpoints of the line.
The value may be any of butt, projecting, or round. Where arrowheads are drawn,
the cap style is ignored.
The default value is butt."""

FILL_COLOR: str = "fill"
"""Specifies the colour to be used to fill item's area.
The given value may be any valid Tk colour.
If the value is an empty string, then the item will not be transparent.
The default value is an empty string."""

RADIUS: str = "radius"
"""Radius of a circle on the tkinter canvas"""

LINE: str = "line"
"""A line element of the ui representation of a section"""

KNOB: str = "knob"
"""A round knob element of the ui representation of a section"""

DEFAULT_SECTION_STYLE = {
    LINE: {FILL_COLOR: "#47936B", LINE_WIDTH: 3},
    KNOB: {FILL_COLOR: "#47936B", LINE_WIDTH: 0, RADIUS: 5},
}

STYLE_UPDATES_SELECTED_SECTION = {
    LINE: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 4},
    KNOB: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 0, RADIUS: 6},
}

# TODO: If possible make this classes reusable for other canvas items
# TODO: Rename to more canvas specific names, as LineSection also has metadata


class SectionGeometryBuilderObserver(ABC):
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
        is_selected: bool = False,
        default_style: dict = DEFAULT_SECTION_STYLE,
        style_updates_selected: dict = STYLE_UPDATES_SELECTED_SECTION,
    ) -> None:  # sourcery skip: dict-assign-update-to-union
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
        style = dict(default_style)
        if is_selected:
            style.update(style_updates_selected)

        print(start)
        print(end)

        self._canvas.create_line(x0, y0, x1, y1, tags=tkinter_tags, **style[LINE])
        self._create_circle(tags=tkinter_tags, x=x0, y=y0, **style[KNOB])
        self._create_circle(tags=tkinter_tags, x=x1, y=y1, **style[KNOB])

    def _create_circle(
        self,
        tags: tuple[str, ...],
        x: int,
        y: int,
        radius: int = 0,
        fill: str = "",
        outline: str = "",
        width: int = 0,
    ) -> None:
        self._canvas.create_oval(
            x - radius,
            y - radius,
            x + radius,
            y + radius,
            fill=fill,
            outline=outline,
            width=width,
            tags=tags,
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


class SectionGeometryBuilder:
    def __init__(
        self,
        observer: SectionGeometryBuilderObserver,
        canvas: AbstractCanvas,
        is_finished: Callable[[list[tuple[int, int]]], bool],
    ) -> None:
        self._observer = observer
        self._is_finished = is_finished

        self.painter = CanvasElementPainter(canvas=canvas)
        self.updater = CanvasElementUpdater(canvas=canvas)
        self.deleter = CanvasElementDeleter(canvas=canvas)

        self._temporary_id: str = TEMPORARY_SECTION_ID
        # self._tmp_end: tuple[int, int] | None = None
        self._coordinates: list[tuple[int, int]] = []

    def set_tmp_end(self, coordinates: tuple[int, int]) -> None:
        if not self.has_start():
            raise ValueError("self.start as to be set before listening to mouse motion")
        self.deleter.delete(tag_or_id="temporary_line_section")
        self.painter.draw(
            tags=["temporary_line_section"],
            id=self._temporary_id,
            start=self._start(),
            end=coordinates,
            is_selected=True,
        )
        # self._tmp_end = coordinates

    def has_start(self) -> bool:
        return len(self._coordinates) >= 1

    def _start(self) -> tuple[int, int]:
        if len(self._coordinates) > 0:
            return self._coordinates[0]
        raise MissingCoordinate("Start coordinate missing")

    def _end(self) -> tuple[int, int]:
        if len(self._coordinates) > 1:
            return self._coordinates[-1]
        raise MissingCoordinate("End coordinate missing")

    def add_coordinate(self, coordinate: tuple[int, int]) -> None:
        self._coordinates.append(coordinate)
        if self._is_finished(self._coordinates):
            self._finish_building()

    def _finish_building(self) -> None:
        self._observer.finish_building(self._coordinates)
        self.deleter.delete(tag_or_id="temporary_line_section")


class MissingCoordinate(Exception):
    pass


class SectionBuilder(SectionGeometryBuilderObserver, CanvasObserver):
    def __init__(
        self,
        viewmodel: ViewModel,
        canvas: AbstractCanvas,
        section: Optional[Section] = None,
    ) -> None:
        self._viewmodel = viewmodel
        self._canvas = canvas
        self.attach_to(self._canvas.event_handler)
        self.geometry_builder = SectionGeometryBuilder(
            observer=self,
            canvas=self._canvas,
            is_finished=self._is_line_finished,
        )
        self._name: Optional[str] = None
        self._coordinates: list[tuple[int, int]] = []
        self._metadata: dict = {}
        self._initialise_with(section)

    def _is_line_finished(self, coordinates: list[tuple[int, int]]) -> bool:
        return len(coordinates) == 2

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
        if (not self.geometry_builder.has_start()) and (
            event_type == "left_mousebutton_up"
        ):
            self.geometry_builder.add_coordinate(coordinate)
        elif self.geometry_builder.has_start() and event_type == "mouse_motion":
            self.geometry_builder.set_tmp_end(coordinate)
        elif self.geometry_builder.has_start() and event_type == "left_mousebutton_up":
            self.geometry_builder.add_coordinate(coordinate)
            self.detach_from(self._canvas.event_handler)

    def finish_building(
        self,
        coordinates: list[tuple[int, int]],
    ) -> None:
        """Sets a line section geometry from the GeometryBuilder and triggers
        further tasks.

        Args:
            start (tuple[int, int]): Tuple of the sections start coordinates
            end (tuple[int, int]): Tuple of the sections end coordinates
        """
        self._coordinates = coordinates
        if (
            ID not in self._metadata
            or RELATIVE_OFFSET_COORDINATES not in self._metadata
        ):
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
        relative_offset_coordinates_enter = self._metadata[RELATIVE_OFFSET_COORDINATES][
            EventType.SECTION_ENTER.serialize()
        ]
        line_section = LineSection(
            id=SectionId(name),
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(
                    **relative_offset_coordinates_enter
                )
            },
            plugin_data={},
            start=self._to_coordinate(self._start()),
            end=self._to_coordinate(self._end()),
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

    def _to_coordinate(self, coordinate: tuple[int, int]) -> Coordinate:
        return Coordinate(coordinate[0], coordinate[1])
