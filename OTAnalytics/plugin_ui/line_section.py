# from customtkinter import CTkFrame

from abc import ABC, abstractmethod

from OTAnalytics.plugin_ui.abstract_canvas_background import AbstractCanvasBackground
from OTAnalytics.plugin_ui.canvas_observer import CanvasObserver
from OTAnalytics.plugin_ui.helpers import get_widget_position
from OTAnalytics.plugin_ui.toplevel_sections import ToplevelSections
from OTAnalytics.plugin_ui.view_model import ViewModel

# from OTAnalytics.plugin_ui.state import StateChanger

TEMPORARY_SECTION_ID: str = "temporary_section"
LINE_WIDTH: int = 4
LINE_COLOR: str = "lightgreen"

# TODO: If possible make this classes reusable for other canvas items
# TODO: Rename to more canvas specific names, as LineSection also has metadata


class LineSectionGeometryBuilderObserver(ABC):
    @abstractmethod
    def set_section_geometry(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> None:
        """
        Receive line section start and end coordinates from LineSectionGeometryBuilder.
        """
        raise NotImplementedError


class LineSectionGeometryPainter:
    def __init__(self, canvas: AbstractCanvasBackground) -> None:
        self._canvas = canvas

    def draw_section(
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


class LineSectionGeometryUpdater:
    def __init__(self, canvas: AbstractCanvasBackground) -> None:
        self._canvas = canvas

    def update_section(
        self, id: str, start: tuple[int, int], end: tuple[int, int]
    ) -> None:
        x0, y0 = start
        x1, y1 = end
        self._canvas.coords(id, x0, y0, x1, y1)


class LineSectionGeometryDeleter:
    def __init__(self, canvas: AbstractCanvasBackground) -> None:
        self._canvas = canvas

    def delete_sections(self, tag_or_id: str) -> None:
        """If a tag is given, deletes all sections from a self._canvas with a given tag.
        If an id is given, deletes the section with this id.

        Args:
            tag (str): Tag given when creating a canvas item (e.g. "line_section")
        """
        self._canvas.delete(tag_or_id)


class LineSectionGeometryBuilder(CanvasObserver):
    def __init__(
        self,
        observer: LineSectionGeometryBuilderObserver,
        canvas: AbstractCanvasBackground,
        # frames_to_disable: list[CTkFrame],
    ) -> None:
        self._observer = observer
        self._canvas = canvas
        # self._frames_to_disable = frames_to_disable

        self.line_section_drawer = LineSectionGeometryPainter(canvas=canvas)
        self.line_section_updater = LineSectionGeometryUpdater(canvas=canvas)
        self.line_section_deleter = LineSectionGeometryDeleter(canvas=canvas)

        self._temporary_id: str = TEMPORARY_SECTION_ID
        self._start: tuple[int, int] | None = None
        self._tmp_end: tuple[int, int] | None = None
        self._end: tuple[int, int] | None = None

        self._setup()

    def _setup(self) -> None:
        self.attach_to(self._canvas.event_handler)
        # self.gui_state_changer = StateChanger()
        # self.gui_state_changer.disable_frames(frames=self._frames_to_disable)

    def update(self, coordinates: tuple[int, int], event_type: str) -> None:
        """Receives and reacts to updates issued by the canvas event handler

        Args:
            coordinates (tuple[int, int]): Coordinates clicked on canvas
            event_type (str): Event type of canvas click
        """
        if self._start is None and event_type == "left_mousebutton_up":
            self._set_start(coordinates)
        elif self._start is not None and event_type == "mouse_motion":
            self._set_tmp_end(coordinates)
        elif self._start is not None and event_type == "left_mousebutton_up":
            self._set_end(coordinates)

    def _set_start(self, coordinates: tuple[int, int]) -> None:
        self._start = coordinates

    def _set_tmp_end(self, coordinates: tuple[int, int]) -> None:
        if self._start is None:
            raise ValueError("self.start as to be set before listening to mouse motion")
        if self._tmp_end is None:
            self.line_section_drawer.draw_section(
                tags=["temporary_line_section"],
                id=self._temporary_id,
                start=self._start,
                end=coordinates,
                line_color="red",
            )
        else:
            self.line_section_updater.update_section(
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
        self._observer.set_section_geometry(self._start, self._end)
        self._teardown()

    def _teardown(self) -> None:
        self.detach_from(self._canvas.event_handler)
        self.line_section_deleter.delete_sections(tag_or_id="temporary_line_section")
        # self.gui_state_changer.reset_states()


class LineSectionBuilder(LineSectionGeometryBuilderObserver):
    def __init__(
        self,
        viewmodel: ViewModel,
        canvas: AbstractCanvasBackground,
    ) -> None:
        self._viewmodel = viewmodel
        self._canvas = canvas
        self.geometry_builder = LineSectionGeometryBuilder(
            observer=self, canvas=self._canvas
        )

        self._start: tuple[int, int] | None = None
        self._end: tuple[int, int] | None = None
        self._name: str | None = None
        self._metadata: dict[str, str] = {}

    def set_section_geometry(
        self, start: tuple[int, int], end: tuple[int, int]
    ) -> None:
        self._start = start
        self._end = end
        self._get_metadata()

    def _get_metadata(self) -> None:
        toplevel_position = get_widget_position(widget=self._canvas)
        self._metadata = ToplevelSections(
            title="New section", initial_position=toplevel_position
        ).get_metadata()
        self._finish_building()

    def _finish_building(self) -> None:
        if self._start is None or self._end is None:
            raise ValueError("Start and end of line_section are not defined")
        if self._metadata == {}:
            raise ValueError("Metadata of line_section are not defined")
        self._viewmodel.set_new_section(
            metadata=self._metadata, start=self._start, end=self._end
        )
