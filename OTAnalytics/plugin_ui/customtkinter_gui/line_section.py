# from customtkinter import CTkFrame

from abc import ABC, abstractmethod
from typing import Optional

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
from OTAnalytics.plugin_ui.customtkinter_gui.constants import (
    DELETE_KEYS,
    ESCAPE_KEY,
    LEFT_BUTTON_UP,
    MOTION,
    RETURN_KEY,
    RIGHT_BUTTON_UP,
)
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import get_widget_position
from OTAnalytics.plugin_ui.customtkinter_gui.style import (
    KNOB,
    KNOB_CORE,
    KNOB_PERIMETER,
    LINE,
)
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_sections import ToplevelSections

TEMPORARY_SECTION_ID: str = "temporary_section"
PRE_EDIT_SECTION_ID: str = "pre_edit_section"
KNOB_INDEX_TAG_PREFIX: str = "knob-index-"

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
        id: str,
        coordinates: list[tuple[int, int]],
        section_style: dict,
        highlighted_knob_index: int | None = None,
        highlighted_knob_style: dict | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """Draws a line section on a canvas.

        Args:
            id (str): ID of the line section.
                Shall be unique among all sections on the canvas.
            coordinates (list[tuple[int, int]]): Knob coordinates that define a section.
            section_style (dict): Dict of style options for tkinter canvas items.
            highlighted_knob_index (int | None, optional): Index of a knob coordinate
                that should be highlighted with a unique style.
                Defaults to None.
            highlighted_knob_style (dict | None, optional): Dict of style options for a
                knob coordinate that should be highlighted with a unique style.
                Defaults to None.
            tags (list[str] | None, optional): Tags to specify groups of line_sections.
                Defaults to None.
        """
        tkinter_tags = (id,) + tuple(tags) if tags is not None else (id,)

        start: tuple[int, int] | None = None
        for index, coordinate in enumerate(coordinates):
            if start is not None:
                self._canvas.create_line(
                    start[0],
                    start[1],
                    coordinate[0],
                    coordinate[1],
                    tags=tkinter_tags + (LINE,),
                    **section_style[LINE],
                )

            knob_style = None
            if index == highlighted_knob_index and highlighted_knob_style is not None:
                knob_style = highlighted_knob_style
            elif KNOB in section_style or highlighted_knob_style is not None:
                knob_style = section_style[KNOB]
            if knob_style is not None:
                self._draw_knob(tkinter_tags, index, coordinate, knob_style)
            start = coordinate

    def _draw_knob(
        self,
        tkinter_tags: tuple[str, ...],
        index: int,
        coordinate: tuple[int, int],
        knob_style: dict,
    ) -> None:
        if KNOB_CORE in knob_style:
            self._draw_circle(
                tags=(tkinter_tags + (KNOB_CORE, f"{KNOB_INDEX_TAG_PREFIX}{index}")),
                x=coordinate[0],
                y=coordinate[1],
                **knob_style[KNOB_CORE],
            )
        if KNOB_PERIMETER in knob_style:
            self._draw_circle(
                tags=tkinter_tags + (KNOB_PERIMETER,),
                x=coordinate[0],
                y=coordinate[1],
                **knob_style[KNOB_PERIMETER],
            )

    def _draw_circle(
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


class CanvasElementDeleter:
    def __init__(self, canvas: AbstractCanvas) -> None:
        self._canvas = canvas

    def delete(self, tag_or_id: str) -> None:
        """Deletes all elements from a canvas with a given tag or id.

        Args:
            tag_or_id (str): Tag or id given when creating a canvas item
                (e.g. "line_section" as a tag or the id of a section as an id)
        """
        self._canvas.delete(tag_or_id)


class SectionKnobEditor:
    def __init__(self, coordinate: tuple[int, int]):
        self._initial_coordinate = coordinate


class SectionGeometryEditor(CanvasObserver):
    # TODO: Split responsibilities in SectionGeometryEditor and SectionKnobEditor
    def __init__(
        self,
        viewmodel: ViewModel,
        canvas: AbstractCanvas,
        section: Section,
        edited_section_style: dict,
        pre_edit_section_style: dict,
        selected_knob_style: dict,
        hovered_knob_style: dict | None = None,
    ) -> None:
        self._viewmodel = viewmodel
        self._canvas = canvas
        self._section = section
        self._pre_edited_section_style = edited_section_style
        self._pre_edit_section_style = pre_edit_section_style
        self._hovered_knob_style = hovered_knob_style
        self._selected_knob_style = selected_knob_style

        self._hovered_knob_index: int | None = None
        self._selected_knob_index: int | None = None
        self._temporary_id: str = TEMPORARY_SECTION_ID
        self._pre_edit_id: str = PRE_EDIT_SECTION_ID

        self.attach_to(self._canvas.event_handler)

        self._get_coordinates()
        self._get_name()
        self._get_matadata()

        self.painter = CanvasElementPainter(canvas=canvas)
        self.deleter = CanvasElementDeleter(canvas=canvas)

        self.painter.draw(
            id=self._pre_edit_id,
            coordinates=self._temporary_coordinates,
            section_style=self._pre_edit_section_style,
        )
        self.painter.draw(
            id=self._temporary_id,
            coordinates=self._temporary_coordinates,
            section_style=self._pre_edited_section_style,
        )

    def _get_coordinates(self) -> None:
        self._coordinates = [
            (int(coordinate.x), int(coordinate.y))
            for coordinate in self._section.get_coordinates()
        ]
        self._temporary_coordinates = self._coordinates.copy()

    def _get_name(self) -> None:
        self._name = self._section.id.id

    def _get_matadata(self) -> None:
        self._metadata = self._section.to_dict()

    def update(self, coordinate: tuple[int, int], event_type: str) -> None:
        """Receives and reacts to updates issued by the canvas event handler

        Args:
            coordinates (tuple[int, int]): Coordinates clicked on canvas
            event_type (str): Event type of canvas click
        """
        if self._selected_knob_index is None:
            if event_type == MOTION:
                self._hover_knob(coordinate)
            elif event_type == LEFT_BUTTON_UP and self._hovered_knob_index is not None:
                self._select_knob()
            elif event_type in {RETURN_KEY, RIGHT_BUTTON_UP}:
                self._finish()
                self.detach_from(self._canvas.event_handler)
            elif event_type == ESCAPE_KEY:
                self._abort()
                self.detach_from(self._canvas.event_handler)
        elif event_type == MOTION:
            self._move_knob(coordinate)
        elif event_type == LEFT_BUTTON_UP:
            self._update_knob(coordinate)
            self._deselect_knob()
        elif event_type == DELETE_KEYS:
            self._delete_selected_knob()
        elif event_type == ESCAPE_KEY:
            self._deselect_knob()

    def _hover_knob(self, coordinate: tuple[int, int]) -> None:
        closest_knob_index = self._get_closest_knob_index(coordinate=coordinate)
        self._hovered_knob_index = closest_knob_index
        if closest_knob_index is not None:
            self._redraw_temporary_section(
                highlighted_knob_index=closest_knob_index,
                highlighted_knob_style=self._hovered_knob_style,
            )
        else:
            self._redraw_temporary_section()

    def _select_knob(self) -> None:
        self._selected_knob_index = self._hovered_knob_index
        if self._selected_knob_index is not None:
            self._redraw_temporary_section(
                highlighted_knob_index=self._selected_knob_index,
                highlighted_knob_style=self._selected_knob_style,
            )

    def _deselect_knob(self) -> None:
        self._selected_knob_index = None
        self._temporary_coordinates = self._coordinates.copy()
        self._redraw_temporary_section(
            highlighted_knob_index=self._hovered_knob_index,
            highlighted_knob_style=self._hovered_knob_style,
        )

    def _move_knob(self, coordinate: tuple[int, int]) -> None:
        if self._selected_knob_index is not None:
            self._update_temporary_coordinates(
                index=self._selected_knob_index, coordinate=coordinate
            )  # TODO: Index instead if coordinate as a class property
            self._redraw_temporary_section(
                highlighted_knob_index=self._selected_knob_index,
                highlighted_knob_style=self._selected_knob_style,
            )

    def _update_knob(self, coordinate: tuple[int, int]) -> None:
        if self._selected_knob_index is not None:
            self._update_coordinates(
                index=self._selected_knob_index, coordinate=coordinate
            )
            self._redraw_temporary_section(
                highlighted_knob_index=self._selected_knob_index
            )

    def _delete_selected_knob(self) -> None:
        if self._selected_knob_index is not None and len(self._coordinates) > 2:
            self._delete_coordinate(index=self._selected_knob_index)
            self._selected_knob_index = None
            self._redraw_temporary_section()

    def _get_closest_knob_index(
        self, coordinate: tuple[int, int], radius: int = 0
    ) -> int | None:  # sourcery skip: inline-immediately-returned-variable
        x, y = coordinate[0], coordinate[1]
        items_of_section = self._canvas.find_withtag(TEMPORARY_SECTION_ID)
        knobs_on_canvas = self._canvas.find_withtag(KNOB_CORE)
        items_in_radius = self._canvas.find_overlapping(
            x - radius, y - radius, x + radius, y + radius
        )
        unordered_knobs_to_consider = tuple(
            set(items_in_radius)
            .intersection(set(items_of_section))
            .intersection(set(knobs_on_canvas))
        )
        ordered_knobs_to_consider = tuple(
            filter(lambda x: x in items_in_radius, unordered_knobs_to_consider)
        )
        if not ordered_knobs_to_consider:
            return None
        closest_knob = ordered_knobs_to_consider[0]
        closest_knob_tags = self._canvas.gettags(closest_knob)
        for tag in closest_knob_tags:
            if KNOB_INDEX_TAG_PREFIX in tag:
                return int(tag.replace(KNOB_INDEX_TAG_PREFIX, ""))
        raise ValueError(
            f"{KNOB_INDEX_TAG_PREFIX} not found in tags of hovered canvas item"
        )

    def _update_temporary_coordinates(
        self, index: int, coordinate: tuple[int, int]
    ) -> None:
        self._temporary_coordinates[index] = coordinate

    def _update_coordinates(self, index: int, coordinate: tuple[int, int]) -> None:
        self._coordinates[index] = coordinate

    def _delete_coordinate(self, index: int) -> None:
        del self._coordinates[index]
        self._temporary_coordinates = self._coordinates.copy()

    def _redraw_temporary_section(
        self,
        highlighted_knob_index: int | None = None,
        highlighted_knob_style: dict | None = None,
    ) -> None:
        self.deleter.delete(tag_or_id=TEMPORARY_SECTION_ID)
        self.painter.draw(
            id=self._temporary_id,
            coordinates=self._temporary_coordinates,
            section_style=self._pre_edited_section_style,
            highlighted_knob_index=highlighted_knob_index,
            highlighted_knob_style=highlighted_knob_style,
        )

    def _finish(self) -> None:
        self._create_section()
        self.deleter.delete(tag_or_id=self._pre_edit_id)
        self.deleter.delete(tag_or_id=self._temporary_id)

    def _to_coordinate(self, coordinate: tuple[int, int]) -> Coordinate:
        return Coordinate(coordinate[0], coordinate[1])

    def _create_section(self) -> None:
        if len(self._coordinates) == 0:
            raise MissingCoordinate("First coordinate is missing")
        elif len(self._coordinates) == 1:
            raise MissingCoordinate("Second coordinate is missing")
        if self._metadata == {}:
            raise ValueError("Metadata of line_section are not defined")
        relative_offset_coordinates_enter = self._metadata[RELATIVE_OFFSET_COORDINATES][
            EventType.SECTION_ENTER.serialize()
        ]
        line_section = LineSection(
            id=SectionId(self._name),
            relative_offset_coordinates={
                EventType.SECTION_ENTER: RelativeOffsetCoordinate(
                    **relative_offset_coordinates_enter
                )
            },
            plugin_data={},
            coordinates=[
                self._to_coordinate(coordinate) for coordinate in self._coordinates
            ],
        )
        self._viewmodel.set_new_section(line_section)

    def _abort(self) -> None:
        self.deleter.delete(tag_or_id=TEMPORARY_SECTION_ID)
        self._viewmodel.refresh_sections_on_gui()


class SectionGeometryBuilder:
    def __init__(
        self,
        observer: SectionGeometryBuilderObserver,
        canvas: AbstractCanvas,
        style: dict,
    ) -> None:
        self._observer = observer
        self._style = style

        self.painter = CanvasElementPainter(canvas=canvas)
        self.deleter = CanvasElementDeleter(canvas=canvas)

        self._temporary_id: str = TEMPORARY_SECTION_ID
        # self._tmp_end: tuple[int, int] | None = None
        self._coordinates: list[tuple[int, int]] = []

    def add_temporary_coordinate(self, coordinate: tuple[int, int]) -> None:
        self.deleter.delete(tag_or_id=TEMPORARY_SECTION_ID)
        self.painter.draw(
            id=self._temporary_id,
            coordinates=self._coordinates + [coordinate],
            section_style=self._style,
        )
        # self._tmp_end = coordinates

    def number_of_coordinates(self) -> int:
        return len(self._coordinates)

    def add_coordinate(self, coordinate: tuple[int, int]) -> None:
        self._coordinates.append(coordinate)

    def finish_building(self) -> None:
        self.deleter.delete(tag_or_id=TEMPORARY_SECTION_ID)
        self.painter.draw(
            id=self._temporary_id,
            coordinates=self._coordinates,
            section_style=self._style,
        )
        self._observer.finish_building(self._coordinates)
        self.deleter.delete(tag_or_id=TEMPORARY_SECTION_ID)

    def abort(self) -> None:
        self.deleter.delete(tag_or_id=TEMPORARY_SECTION_ID)


class MissingCoordinate(Exception):
    pass


class SectionBuilder(SectionGeometryBuilderObserver, CanvasObserver):
    def __init__(
        self,
        viewmodel: ViewModel,
        canvas: AbstractCanvas,
        style: dict,
        section: Optional[Section] = None,
    ) -> None:
        self._viewmodel = viewmodel
        self._canvas = canvas
        self._style = style
        self.attach_to(self._canvas.event_handler)
        self.geometry_builder = SectionGeometryBuilder(
            observer=self,
            canvas=self._canvas,
            style=self._style,
        )
        self._name: Optional[str] = None
        self._coordinates: list[tuple[int, int]] = []
        self._metadata: dict = {}
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
        if event_type == LEFT_BUTTON_UP:
            self.geometry_builder.add_coordinate(coordinate)
        elif event_type == MOTION:
            self.geometry_builder.add_temporary_coordinate(coordinate)
        elif self.geometry_builder.number_of_coordinates() >= 2 and (
            event_type in {RIGHT_BUTTON_UP, RETURN_KEY}
        ):
            self.geometry_builder.finish_building()
            self.detach_from(self._canvas.event_handler)
        elif event_type == ESCAPE_KEY:
            self.geometry_builder.abort()
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
        if not self._metadata[ID]:
            return
        self._create_section()

    def _get_metadata(self) -> None:
        toplevel_position = get_widget_position(widget=self._canvas)
        self._metadata = ToplevelSections(
            title="New section", initial_position=toplevel_position
        ).get_metadata()

    def _create_section(self) -> None:
        if self.number_of_coordinates() == 0:
            raise MissingCoordinate("First coordinate is missing")
        elif self.number_of_coordinates() == 1:
            raise MissingCoordinate("Second coordinate is missing")
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
            coordinates=[
                self._to_coordinate(coordinate) for coordinate in self._coordinates
            ],
        )
        self._viewmodel.set_new_section(line_section)

    def _to_coordinate(self, coordinate: tuple[int, int]) -> Coordinate:
        return Coordinate(coordinate[0], coordinate[1])

    def number_of_coordinates(self) -> int:
        return len(self._coordinates)
