# from customtkinter import CTkFrame

from abc import ABC, abstractmethod
from typing import Optional

from domain.section import ID, Section

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
    def finish_building(self, start: tuple[int, int], end: tuple[int, int]) -> None:
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

    def _set_start(self, coordinates: tuple[int, int]) -> None:
        self._start = coordinates

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

    def _set_end(self, coordinates: tuple[int, int]) -> None:
        self._end = coordinates
        self._finish_building()

    def _finish_building(self) -> None:
        if self._start is None or self._end is None:
            raise ValueError(
                "Both self.start and self.end have to be set to finish building"
            )
        self._observer.finish_building(self._start, self._end)
        self.deleter.delete(tag_or_id="temporary_line_section")


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

        self._start: Optional[tuple[int, int]] = None
        self._end: Optional[tuple[int, int]] = None
        self._name: Optional[str] = None
        self._metadata: dict[str, str] = {}
        self._initialise_with(section)

    def _initialise_with(self, section: Optional[Section]) -> None:
        if template := section:
            start_coordinate = template.get_coordinates()[0]
            end_coordinate = template.get_coordinates()[-1]
            self._start = (start_coordinate.x, start_coordinate.y)
            self._end = (end_coordinate.x, end_coordinate.y)
            self._name = template.id
            self._metadata = template.to_dict()

    def update(self, coordinates: tuple[int, int], event_type: str) -> None:
        """Receives and reacts to updates issued by the canvas event handler

        Args:
            coordinates (tuple[int, int]): Coordinates clicked on canvas
            event_type (str): Event type of canvas click
        """
        if self.geometry_builder._start is None and event_type == "left_mousebutton_up":
            self.geometry_builder._set_start(coordinates)
        elif self.geometry_builder._start is not None and event_type == "mouse_motion":
            self.geometry_builder._set_tmp_end(coordinates)
        elif (
            self.geometry_builder._start is not None
            and event_type == "left_mousebutton_up"
        ):
            self.geometry_builder._set_end(coordinates)
            self.detach_from(self._canvas.event_handler)

    def finish_building(self, start: tuple[int, int], end: tuple[int, int]) -> None:
        """Sets a line section geomatry from the GeometryBuilder and triggers
        further tasks.

        Args:
            start (tuple[int, int]): Tuple of the sections start coordinates
            end (tuple[int, int]): Tuple of the sections end coordinates
        """
        self._start = start
        self._end = end
        if ID not in self._metadata:
            self._get_metadata()
        self._finish_building()

    def _get_metadata(self) -> None:
        toplevel_position = get_widget_position(widget=self._canvas)
        self._metadata = ToplevelSections(
            title="New section", initial_position=toplevel_position
        ).get_metadata()

    def _finish_building(self) -> None:
        if self._start is None or self._end is None:
            raise ValueError("Start and end of line_section are not defined")
        if self._metadata == {}:
            raise ValueError("Metadata of line_section are not defined")
        self._viewmodel.set_new_section(
            metadata=self._metadata, start=self._start, end=self._end
        )
