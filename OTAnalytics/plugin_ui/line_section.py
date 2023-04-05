# from customtkinter import CTkFrame

from OTAnalytics.plugin_ui.abstract_canvas_background import AbstractCanvasBackground
from OTAnalytics.plugin_ui.canvas_observer import CanvasObserver
from OTAnalytics.plugin_ui.section import (
    SectionBuilder,
    SectionDeleter,
    SectionDrawer,
    SectionUpdater,
)
from OTAnalytics.plugin_ui.view_model import ViewModel

# from OTAnalytics.plugin_ui.state import StateChanger

TEMPORARY_SECTION_ID: str = "temporary_section"
LINE_WIDTH: int = 5
LINE_COLOR: str = "red"


class LineSectionBuilder(SectionBuilder, CanvasObserver):
    def __init__(
        self,
        view_model: ViewModel,
        canvas: AbstractCanvasBackground,
        # frames_to_disable: list[CTkFrame],
    ) -> None:
        self._view_model = view_model
        self._canvas = canvas
        # self._frames_to_disable = frames_to_disable

        self.line_section_drawer = LineSectionDrawer(canvas=canvas)
        self.line_section_updater = LineSectionUpdater(canvas=canvas)
        self.line_section_deleter = LineSectionDeleter(canvas=canvas)

        self.temporary_id: str = TEMPORARY_SECTION_ID
        self.point0: tuple[int, int] | None = None
        self.point1_tmp: tuple[int, int] | None = None
        self.point1: tuple[int, int] | None = None

        self.setup()

    def setup(self) -> None:
        self.attach_to(self._canvas.event_handler)
        # self.gui_state_changer = StateChanger()
        # self.gui_state_changer.disable_frames(frames=self._frames_to_disable)

    def update(self, coordinates: tuple[int, int], event_type: str) -> None:
        if self.point0 is None and event_type == "left_mousebutton_up":
            self.set_point0(coordinates)
        elif self.point0 is not None and event_type == "mouse_motion":
            self.set_tmp_point(coordinates)
        elif self.point0 is not None and event_type == "left_mousebutton_up":
            self.set_point1(coordinates)

    def set_point0(self, coordinates: tuple[int, int]) -> None:
        self.point0 = coordinates

    def set_tmp_point(self, coordinates: tuple[int, int]) -> None:
        if self.point0 is None:
            raise ValueError(
                "self.point0 as to be set before listening to mouse motion"
            )
        if self.point1_tmp is None:
            print("No tmp point")
            self.line_section_drawer.draw_section(
                id=self.temporary_id, point0=self.point0, point1=coordinates
            )
        else:
            self.line_section_updater.update_section(
                id=self.temporary_id, point0=self.point0, point1=coordinates
            )
        self.point1_tmp = coordinates

    def set_point1(self, coordinates: tuple[int, int]) -> None:
        self.point1 = coordinates
        self.finish_building()

    def finish_building(self) -> None:
        if self.point0 is None or self.point1 is None:
            raise ValueError(
                "Both self.point0 and self.point1 have to be set to finish building"
            )
        self._view_model.set_new_section_geometry(self.point0, self.point1)
        self.teardown()

    def teardown(self) -> None:
        self.detach_from(self._canvas.event_handler)
        self.line_section_deleter.delete_section(self.temporary_id)
        # self.gui_state_changer.reset_states()


class LineSectionDrawer(SectionDrawer):
    def __init__(self, canvas: AbstractCanvasBackground) -> None:
        self._canvas = canvas

    def draw_section(
        self,
        id: str,
        point0: tuple[int, int],
        point1: tuple[int, int],
        line_width: int = LINE_WIDTH,
        line_color: str = LINE_COLOR,
    ) -> None:
        x0, y0 = point0
        x1, y1 = point1
        self.line_id = self._canvas.create_line(
            x0, y0, x1, y1, width=line_width, fill=line_color, tags=id
        )


class LineSectionUpdater(SectionUpdater):
    def __init__(self, canvas: AbstractCanvasBackground) -> None:
        self._canvas = canvas

    def update_section(
        self, id: str, point0: tuple[int, int], point1: tuple[int, int]
    ) -> None:
        x0, y0 = point0
        x1, y1 = point1
        self._canvas.coords(id, x0, y0, x1, y1)


class LineSectionDeleter(SectionDeleter):
    def __init__(self, canvas: AbstractCanvasBackground) -> None:
        self._canvas = canvas

    def delete_section(self, id: str) -> None:
        self._canvas.delete(id)
