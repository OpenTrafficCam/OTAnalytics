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
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import get_widget_position
from OTAnalytics.plugin_ui.customtkinter_gui.style import KNOB, LINE
from OTAnalytics.plugin_ui.customtkinter_gui.toplevel_sections import ToplevelSections

TEMPORARY_SECTION_ID: str = "temporary_section"

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
        coordinates: list[tuple[int, int]],
        style: dict,
    ) -> None:  # sourcery skip: dict-assign-update-to-union
        """Draws a line section on a canvas.

        Args:
            tag (str): Tag for groups of line_sections
            id (str): ID of the line section. Has to be unique among all line sections.
            start (tuple[int, int]): First point of the line section
            end (tuple[int, int]): Second Point of the line section
            style (dict): Dict of style options for tkinter canvas items.
        """
        tkinter_tags = (id,) + tuple(tags)

        start: tuple[int, int] | None = None
        for coordinate in coordinates:
            if start is not None:
                self._canvas.create_line(
                    start[0],
                    start[1],
                    coordinate[0],
                    coordinate[1],
                    tags=tkinter_tags + (LINE,),
                    **style[LINE],
                )
            if KNOB in style:
                self._create_knob(
                    tags=tkinter_tags + (KNOB,),
                    x=coordinate[0],
                    y=coordinate[1],
                    **style[KNOB],
                )
            start = coordinate

    def _create_knob(
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
            tag (str): Tag given when creating a canvas item (e.g. "line_section")
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
        style: dict,
    ) -> None:
        self._viewmodel = viewmodel
        self._canvas = canvas
        self._section = section
        self._style = style

        self._selected_knob_coordinate: tuple[int, int] | None = None
        self._temporary_id: str = TEMPORARY_SECTION_ID

        self._get_coordinates()
        self._get_name()

        self.painter = CanvasElementPainter(canvas=canvas)
        self.deleter = CanvasElementDeleter(canvas=canvas)

    def _get_coordinates(self) -> None:
        self._coordinates = [
            (int(coordinate.x), int(coordinate.y))
            for coordinate in self._section.get_coordinates()
        ]
        self._temporary_coordinates = self._coordinates.copy()

    def _get_name(self) -> None:
        self._name = self._section.id.id

    def update(self, coordinate: tuple[int, int], event_type: str) -> None:
        """Receives and reacts to updates issued by the canvas event handler

        Args:
            coordinates (tuple[int, int]): Coordinates clicked on canvas
            event_type (str): Event type of canvas click
        """
        print(event_type)
        if event_type == "left_mousebutton_down":
            self._set_selected_knob_coordinate(coordinate)
        elif event_type == "delete" and self._selected_knob_coordinate is not None:
            self._delete_coordinate(coordinate_to_remove=coordinate)
            self._redraw_temporary_section()
        elif (
            event_type == "mouse_motion" and self._selected_knob_coordinate is not None
        ):
            self._update_coordinate(temporary_coordinate=coordinate)
            self._redraw_temporary_section()
        elif (
            event_type == "left_mousebutton_up"
            and self._selected_knob_coordinate is not None
        ):
            self._update_coordinate(temporary_coordinate=coordinate)
            self._redraw_temporary_section()
            self._coordinates = self._temporary_coordinates.copy()
            self._selected_knob_coordinate = None
        elif event_type in {"return", "right_mousebutton_up"}:
            self._finish()
            self.detach_from(self._canvas.event_handler)
        elif event_type == "escape":
            self._abort()
            self.detach_from(self._canvas.event_handler)

    def _set_selected_knob_coordinate(
        self, selected_coordinate: tuple[int, int]
    ) -> None:
        items_of_section = self._canvas.find_withtag(self._name)
        knobs_on_canvas = self._canvas.find_withtag(KNOB)
        items_in_and_by_distance = self._canvas.find_closest(
            x=selected_coordinate[0], y=selected_coordinate[1]
        )
        unordered_knobs_to_consider = tuple(
            set(items_in_and_by_distance)
            .intersection(set(items_of_section))
            .intersection(set(knobs_on_canvas))
        )
        ordered_knobs_to_consider = tuple(
            filter(lambda x: x in items_in_and_by_distance, unordered_knobs_to_consider)
        )
        closest_knob_bbox = self._canvas.coords(ordered_knobs_to_consider[0])
        self._selected_knob_coordinate = (
            closest_knob_bbox[3] - closest_knob_bbox[0],
            closest_knob_bbox[2] - closest_knob_bbox[1],
        )

    def _update_coordinate(self, temporary_coordinate: tuple[int, int]) -> None:
        self._temporary_coordinates = [
            temporary_coordinate if _ == self._selected_knob_coordinate else _
            for _ in self._coordinates
        ]

    def _delete_coordinate(self, coordinate_to_remove: tuple[int, int]) -> None:
        self._temporary_coordinates = [
            _ for _ in self._coordinates if _ != coordinate_to_remove
        ]

    def _redraw_temporary_section(self) -> None:
        self.deleter.delete(tag_or_id="temporary_line_section")
        self.painter.draw(
            tags=["temporary_line_section"],
            id=self._temporary_id,
            coordinates=self._temporary_coordinates,
            style=self._style,
        )

    def _finish(self) -> None:
        self._create_section()

    def _create_section(self) -> None:
        pass  # TODO: See SectionBuilder

    def _abort(self) -> None:
        self.deleter.delete(tag_or_id="temporary_line_section")


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
        if self.number_of_coordinates() == 0:
            raise ValueError(
                "First coordinate has to be set before listening to mouse motion"
            )
        self.deleter.delete(tag_or_id="temporary_line_section")
        self.painter.draw(
            tags=["temporary_line_section"],
            id=self._temporary_id,
            coordinates=self._coordinates + [coordinate],
            style=self._style,
        )
        # self._tmp_end = coordinates

    def number_of_coordinates(self) -> int:
        return len(self._coordinates)

    def add_coordinate(self, coordinate: tuple[int, int]) -> None:
        self._coordinates.append(coordinate)

    def finish_building(self) -> None:
        self.deleter.delete(tag_or_id="temporary_line_section")
        self.painter.draw(
            tags=["temporary_line_section"],
            id=self._temporary_id,
            coordinates=self._coordinates,
            style=self._style,
        )
        self._observer.finish_building(self._coordinates)
        self.deleter.delete(tag_or_id="temporary_line_section")

    def abort(self) -> None:
        self.deleter.delete(tag_or_id="temporary_line_section")


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
        if event_type == "left_mousebutton_up":
            print("left_mousebutton_up")
            self.geometry_builder.add_coordinate(coordinate)
        elif (
            self.geometry_builder.number_of_coordinates() >= 1
            and event_type == "mouse_motion"
        ):
            self.geometry_builder.add_temporary_coordinate(coordinate)
        elif self.geometry_builder.number_of_coordinates() >= 2 and (
            event_type in {"right_mousebutton_up", "return"}
        ):
            print("right_mousebutton_up")
            self.geometry_builder.finish_building()
            self.detach_from(self._canvas.event_handler)
        elif event_type == "escape":
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
