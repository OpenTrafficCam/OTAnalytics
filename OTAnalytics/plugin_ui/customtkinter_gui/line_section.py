import asyncio
import tkinter
from abc import ABC, abstractmethod
from typing import Optional

from OTAnalytics.adapter_ui.flow_adapter import SectionRefPointCalculator
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.domain.geometry import Coordinate
from OTAnalytics.domain.section import Section
from OTAnalytics.plugin_ui.customtkinter_gui.abstract_ctk_canvas import (
    AbstractCTkCanvas,
)
from OTAnalytics.plugin_ui.customtkinter_gui.canvas_observer import CanvasObserver
from OTAnalytics.plugin_ui.customtkinter_gui.constants import (
    DELETE_KEYS,
    ESCAPE_KEY,
    LEFT_BUTTON_UP,
    LEFT_KEY,
    MOTION,
    MOTION_WHILE_LEFT_BUTTON_DOWN,
    PLUS_KEYS,
    RETURN_KEY,
    RIGHT_BUTTON_UP,
    RIGHT_KEY,
)
from OTAnalytics.plugin_ui.customtkinter_gui.helpers import coordinate_is_on_widget
from OTAnalytics.plugin_ui.customtkinter_gui.style import (
    KNOB,
    KNOB_CORE,
    KNOB_PERIMETER,
    LINE,
    SECTION_TEXT,
)

TEMPORARY_SECTION_ID: str = "temporary_section"
PRE_EDIT_SECTION_ID: str = "pre_edit_section"
KNOB_INDEX_TAG_PREFIX: str = "knob-index-"


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


class ArrowPainter:
    def __init__(self, canvas: AbstractCTkCanvas) -> None:
        self._canvas = canvas

    def draw(
        self,
        start_section: Section,
        end_section: Section,
        start_refpt_calculator: SectionRefPointCalculator,
        end_refpt_calculator: SectionRefPointCalculator,
        arrow_style: dict | None = None,
        tags: list[str] | None = None,
    ) -> None:
        start_x, start_y = start_refpt_calculator.get_reference_point(start_section)
        end_x, end_y = end_refpt_calculator.get_reference_point(end_section)
        self._canvas.create_line(
            start_x,
            start_y,
            end_x,
            end_y,
            arrow=tkinter.LAST,
            tags=tags,
            **arrow_style,
        )


class SectionPainter:
    def __init__(self, canvas: AbstractCTkCanvas) -> None:
        self._canvas = canvas

    def draw(
        self,
        id: str,
        coordinates: list[tuple[int, int]],
        section_style: dict,
        is_area_section: bool = False,
        highlighted_knob_index: int | None = None,
        highlighted_knob_style: dict | None = None,
        text: str | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """Draws a line section on a canvas.

        Args:
            id (str): ID of the line section.
                Shall be unique among all sections on the canvas.
            coordinates (list[tuple[int, int]]): Knob coordinates that define a section.
            section_style (dict): Dict of style options for tkinter canvas items.
            area_section (bool): True, if the section is an area section.
                False if the seciton is a line section.
                Defaults to False.
            highlighted_knob_index (int | None, optional): Index of a knob coordinate
                that should be highlighted with a unique style.
                Defaults to None.
            highlighted_knob_style (dict | None, optional): Dict of style options for a
                knob coordinate that should be highlighted with a unique style.
                Defaults to None.
            text (str | None, optional): Text to display above the section.
                Defaults to None.
            tags (list[str] | None, optional): Tags to specify groups of line_sections.
                Defaults to None.
        """
        tkinter_tags = (id,) + tuple(tags) if tags is not None else (id,)

        self._draw_geometries(
            coordinates,
            section_style,
            is_area_section,
            highlighted_knob_index,
            highlighted_knob_style,
            tkinter_tags,
        )

        if text is not None:
            text_position = coordinates[0]
            self._draw_text(text, text_position, tkinter_tags)

    def _draw_geometries(
        self,
        coordinates: list[tuple[int, int]],
        section_style: dict,
        is_area_section: bool,
        highlighted_knob_index: int | None,
        highlighted_knob_style: dict | None,
        tkinter_tags: tuple[str, ...],
    ) -> None:
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

        if is_area_section and len(coordinates) > 2:
            self._extend_to_polygon(coordinates, section_style, tkinter_tags)

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

    def _extend_to_polygon(
        self,
        coordinates: list[tuple[int, int]],
        section_style: dict,
        tkinter_tags: tuple[str, ...],
    ) -> None:
        start = coordinates[-1]
        end = coordinates[0]
        self._canvas.create_line(
            start[0],
            start[1],
            end[0],
            end[1],
            tags=tkinter_tags + (LINE,),
            **section_style[LINE],
        )

    def _draw_text(
        self,
        text: str,
        text_position: tuple[float, float],
        tkinter_tags: tuple[str, ...],
    ) -> None:
        x, y = text_position
        self._canvas.create_text(x, y, text=text, tags=tkinter_tags + (SECTION_TEXT,))


class CanvasElementDeleter:
    def __init__(self, canvas: AbstractCTkCanvas) -> None:
        self._canvas = canvas

    def delete(self, tag_or_id: str) -> None:
        """Deletes all elements from a canvas with a given tag or id.

        Args:
            tag_or_id (str): Tag or id given when creating a canvas item
                (e.g. "line_section" as a tag or the id of a section as an id)
        """
        self._canvas.delete(tag_or_id)


def add_last_coordinate(
    is_area_section: bool, coordinates: list[tuple[int, int]]
) -> list[tuple[int, int]]:
    """
    For area sections, the first and last coordinate are equal. Therefore, this
    method addds the first coordinate as the last one, if the section is an area.

    Args:
        is_area_section (bool): should coordinates form an area
        coordinates (list[tuple[int, int]]): coordinates to form a line or an area

    Returns:
        list[tuple[int, int]]: coordinates to forma a line or an area
    """
    return coordinates + [coordinates[0]] if is_area_section else coordinates


class SectionGeometryEditor(CanvasObserver):
    def __init__(
        self,
        viewmodel: ViewModel,
        canvas: AbstractCTkCanvas,
        section: Section,
        edited_section_style: dict,
        pre_edit_section_style: dict,
        selected_knob_style: dict,
        hovered_knob_style: dict | None = None,
        is_area_section: bool = False,
    ) -> None:
        self._viewmodel = viewmodel
        self._canvas = canvas
        self._section = section
        self._is_area_section = is_area_section
        self._edited_section_style = edited_section_style
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

        self.painter = SectionPainter(canvas=canvas)
        self.deleter = CanvasElementDeleter(canvas=canvas)

        self.painter.draw(
            id=self._pre_edit_id,
            coordinates=self._temporary_coordinates,
            section_style=self._pre_edit_section_style,
            is_area_section=self._is_area_section,
        )
        self.painter.draw(
            id=self._temporary_id,
            coordinates=self._temporary_coordinates,
            section_style=self._edited_section_style,
            is_area_section=self._is_area_section,
        )

    def _get_coordinates(self) -> None:
        coordinates = [
            (int(coordinate.x), int(coordinate.y))
            for coordinate in self._section.get_coordinates()
        ]
        self._coordinates = self.drop_last_coordinate(coordinates)
        self._temporary_coordinates = self._coordinates.copy()

    def drop_last_coordinate(
        self, coordinates: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        """
        If the section is an area section, the first and the last coordinates are same.
        To visualize an area section, the last coordinate has to be removed.

        Args:
            coordinates (list[tuple[int, int]]): coordinates to visualize

        Returns:
            list[tuple[int, int]]: coordinates to visualize
        """
        return coordinates[:-1] if self._is_area_section else coordinates

    def _get_name(self) -> None:
        self._name = self._section.id.id

    def _get_matadata(self) -> None:
        self._metadata = self._section.to_dict()

    def update(
        self, coordinate: tuple[int, int], event_type: str, key: str | None
    ) -> None:
        """Receives and reacts to updates issued by the canvas event handler

        Args:
            coordinates (tuple[int, int]): Coordinates clicked on canvas
            event_type (str): Type of event while mouse was on canvas.
            key (str | None): Key character that has been pressed while mouse was on
                canvas.
        """
        if self._selected_knob_index is None:
            if event_type == MOTION:
                self._hover_knob(coordinate)
            elif event_type == LEFT_BUTTON_UP and self._hovered_knob_index is not None:
                self._select_hovered_knob()
            elif event_type == PLUS_KEYS:
                self._add_knob(coordinate=coordinate)
            elif event_type in {RETURN_KEY, RIGHT_BUTTON_UP}:
                self.detach_from(self._canvas.event_handler)
                self._finish()
            elif event_type == ESCAPE_KEY:
                self.detach_from(self._canvas.event_handler)
                self._abort()
                self._viewmodel.cancel_action()
        elif event_type == LEFT_KEY:
            self._shift_selected_knob_backward()
        elif event_type == RIGHT_KEY:
            self._shift_selected_knob_forward()
        elif event_type in [
            MOTION,
            MOTION_WHILE_LEFT_BUTTON_DOWN,
        ] and coordinate_is_on_widget(coordinate, self._canvas):
            self._move_knob(coordinate)
        elif event_type == LEFT_BUTTON_UP and coordinate_is_on_widget(
            coordinate, self._canvas
        ):
            self._update_knob(coordinate)
            self._deselect_knob()
        elif event_type == DELETE_KEYS:
            self._delete_selected_knob()
        elif event_type == ESCAPE_KEY:
            self._deselect_knob()
            self._viewmodel.cancel_action()

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

    def _select_hovered_knob(self) -> None:
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
            self._update_temporary_coordinate(
                index=self._selected_knob_index, coordinate=coordinate
            )
            self._redraw_temporary_section(
                highlighted_knob_index=self._selected_knob_index,
                highlighted_knob_style=self._selected_knob_style,
            )

    def _add_knob(self, coordinate: tuple[int, int]) -> None:
        self._append_temporary_coordinate(coordinate=coordinate)
        self._selected_knob_index = len(self._temporary_coordinates) - 1
        self._redraw_temporary_section(
            highlighted_knob_index=self._selected_knob_index,
            highlighted_knob_style=self._selected_knob_style,
        )

    def _shift_selected_knob_forward(self) -> None:
        i = self._selected_knob_index
        if i is None or i > len(self._temporary_coordinates) - 1:
            return
        elif i == len(self._temporary_coordinates) - 1:
            if not self._is_area_section:
                return
            self._swap_temporary_coordinates(index=i, index_other=0)
            self._selected_knob_index = 0
        else:
            self._swap_temporary_coordinates(index=i, index_other=i + 1)
            self._selected_knob_index = i + 1
        self._redraw_temporary_section(
            highlighted_knob_index=self._selected_knob_index,
            highlighted_knob_style=self._selected_knob_style,
        )

    def _shift_selected_knob_backward(self) -> None:
        i = self._selected_knob_index
        if i is None or i < 0:
            return
        elif i == 0:
            if not self._is_area_section:
                return
            self._swap_temporary_coordinates(
                index=i, index_other=len(self._temporary_coordinates) - 1
            )
            self._selected_knob_index = len(self._temporary_coordinates) - 1
        else:
            self._swap_temporary_coordinates(index=i, index_other=i - 1)
            self._selected_knob_index = i - 1
        self._redraw_temporary_section(
            highlighted_knob_index=self._selected_knob_index,
            highlighted_knob_style=self._selected_knob_style,
        )

    def _update_knob(self, coordinate: tuple[int, int]) -> None:
        if self._selected_knob_index is not None:
            self._update_coordinates()
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
    ) -> int | None:
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

    def _update_temporary_coordinate(
        self, index: int, coordinate: tuple[int, int]
    ) -> None:
        self._temporary_coordinates[index] = coordinate

    def _swap_temporary_coordinates(self, index: int, index_other: int) -> None:
        (
            self._temporary_coordinates[index],
            self._temporary_coordinates[index_other],
        ) = (
            self._temporary_coordinates[index_other],
            self._temporary_coordinates[index],
        )

    def _append_temporary_coordinate(self, coordinate: tuple[int, int]) -> None:
        self._temporary_coordinates.append(coordinate)

    def _update_coordinates(self) -> None:
        self._coordinates = self._temporary_coordinates.copy()

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
            section_style=self._edited_section_style,
            highlighted_knob_index=highlighted_knob_index,
            highlighted_knob_style=highlighted_knob_style,
            is_area_section=self._is_area_section,
        )

    def _finish(self) -> None:
        self._update_section()
        self.deleter.delete(tag_or_id=self._pre_edit_id)
        self.deleter.delete(tag_or_id=self._temporary_id)

    def _to_coordinate(self, coordinate: tuple[int, int]) -> Coordinate:
        return Coordinate(coordinate[0], coordinate[1])

    def _update_section(self) -> None:
        coordinates = add_last_coordinate(self._is_area_section, self._coordinates)
        self._viewmodel.update_section_coordinates(self._metadata, coordinates)

    def _abort(self) -> None:
        self.deleter.delete(tag_or_id=TEMPORARY_SECTION_ID)
        self._viewmodel.refresh_items_on_canvas()


class SectionGeometryBuilder:
    def __init__(
        self,
        observer: SectionGeometryBuilderObserver,
        canvas: AbstractCTkCanvas,
        is_area_section: bool,
        style: dict,
    ) -> None:
        self._observer = observer
        self._is_area_section = is_area_section
        self._style = style

        self.painter = SectionPainter(canvas=canvas)
        self.deleter = CanvasElementDeleter(canvas=canvas)

        self._temporary_id: str = TEMPORARY_SECTION_ID
        self._coordinates: list[tuple[int, int]] = []

    def add_temporary_coordinate(self, coordinate: tuple[int, int]) -> None:
        self.deleter.delete(tag_or_id=TEMPORARY_SECTION_ID)
        self.painter.draw(
            id=self._temporary_id,
            coordinates=self._coordinates + [coordinate],
            section_style=self._style,
            is_area_section=self._is_area_section,
        )

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
            is_area_section=self._is_area_section,
        )
        self._observer.finish_building(self._coordinates)
        self.deleter.delete(tag_or_id=TEMPORARY_SECTION_ID)

    def abort(self) -> None:
        self.deleter.delete(tag_or_id=TEMPORARY_SECTION_ID)


class SectionBuilder(SectionGeometryBuilderObserver, CanvasObserver):
    def __init__(
        self,
        viewmodel: ViewModel,
        canvas: AbstractCTkCanvas,
        style: dict,
        is_area_section: bool = False,
        section: Optional[Section] = None,
    ) -> None:
        self._viewmodel = viewmodel
        self._canvas = canvas
        self._style = style
        self._is_area_section = is_area_section
        self.attach_to(self._canvas.event_handler)
        self.geometry_builder = SectionGeometryBuilder(
            observer=self,
            canvas=self._canvas,
            style=self._style,
            is_area_section=self._is_area_section,
        )
        self._id: Optional[str] = None
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
            self._id = template.id.id
            self._name = template.name
            self._metadata = template.to_dict()

    def update(
        self, coordinate: tuple[int, int], event_type: str, key: str | None
    ) -> None:
        """Receives and reacts to updates issued by the canvas event handler

        Args:
            coordinates (tuple[int, int]): Coordinates clicked on canvas
            event_type (str): Type of event while mouse was on canvas.
            key (str | None): Key character that has been pressed while mouse was on
                canvas.
        """
        if event_type == LEFT_BUTTON_UP and coordinate_is_on_widget(
            coordinate, self._canvas
        ):
            self.geometry_builder.add_coordinate(coordinate)
        elif event_type in [
            MOTION,
            MOTION_WHILE_LEFT_BUTTON_DOWN,
        ] and coordinate_is_on_widget(coordinate, self._canvas):
            self.geometry_builder.add_temporary_coordinate(coordinate)
        elif self.geometry_builder.number_of_coordinates() >= 2 and (
            event_type in {RIGHT_BUTTON_UP, RETURN_KEY}
        ):
            self.detach_from(self._canvas.event_handler)
            self.geometry_builder.finish_building()
        elif event_type == ESCAPE_KEY:
            self.detach_from(self._canvas.event_handler)
            self.geometry_builder.abort()
            self._viewmodel.cancel_action()

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
        self._create_section()

    async def _get_metadata(self) -> dict:
        toplevel_position = self._canvas.get_position()
        return await self._viewmodel.get_section_metadata(
            title="Add section", initial_position=toplevel_position
        )

    def _create_section(self) -> None:
        coordinates = add_last_coordinate(self._is_area_section, self._coordinates)
        asyncio.run(
            self._viewmodel.add_new_section(
                coordinates=coordinates,
                is_area_section=self._is_area_section,
                get_metadata=self._get_metadata,
            )
        )
