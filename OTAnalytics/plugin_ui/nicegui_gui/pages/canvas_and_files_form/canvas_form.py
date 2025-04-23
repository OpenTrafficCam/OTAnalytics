from typing import Iterable, Optional, Self

from nicegui import events, ui
from nicegui.elements.interactive_image import InteractiveImage
from nicegui.events import KeyEventArguments
from PIL import Image

from OTAnalytics.adapter_ui.abstract_canvas import TAG_SELECTED_SECTION, AbstractCanvas
from OTAnalytics.adapter_ui.abstract_frame_canvas import AbstractFrameCanvas
from OTAnalytics.adapter_ui.abstract_treeview_interface import AbstractTreeviewInterface
from OTAnalytics.adapter_ui.flow_adapter import SectionRefPointCalculator
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.resources.resource_manager import (
    CanvasKeys,
    HotKeys,
    ResourceManager,
)
from OTAnalytics.domain.section import Section
from OTAnalytics.domain.track import TrackImage
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.circle import Circle
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.circle_resources import (
    CircleResources,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line import Line
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line_resources import LineResources
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polyline import Polyline
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.section_resources import (
    SectionResource,
)

NORMAL_COLOR = "green"
SELECTED_COLOR = "red"
EDIT_COLOR = "orange"
MOVING_COLOR = "blue"
MOVING_STROKE_WIDTH = 400
MOVING_STROKE_OPACITY = 0.0


CLICK = "click"
POINTER_EVENT_ALL = "all"
POINTER_EVENT_NONE = ""
IMAGE_X = "image_x"
IMAGE_Y = "image_y"
ELEMENT_ID = "element_id"

CURSOR = "pointer"
NEW_SECTION_ID = "new-section-id"


def circle_to_coordinates(circles: Iterable[Circle]) -> list[tuple[int, int]]:
    return [circle.to_tuple() for circle in circles]


def create_circle(e: dict, fill: str = NORMAL_COLOR) -> Circle:
    return Circle(
        x=round(e[IMAGE_X]),
        y=round(e[IMAGE_Y]),
        pointer_event=POINTER_EVENT_ALL,
        id=e[ELEMENT_ID],
        fill=fill,
    )


def create_moving_circle(e: dict, fill: str = NORMAL_COLOR) -> Circle:
    return Circle(
        x=round(e[IMAGE_X]),
        y=round(e[IMAGE_Y]),
        pointer_event=POINTER_EVENT_ALL,
        id=e[ELEMENT_ID],
        fill=fill,
        stroke=MOVING_COLOR,
        stroke_width=MOVING_STROKE_WIDTH,
        stroke_opacity=MOVING_STROKE_OPACITY,
    )


class CanvasForm(AbstractCanvas, AbstractFrameCanvas, AbstractTreeviewInterface):

    def __init__(
        self,
        viewmodel: ViewModel,
        resource_manager: ResourceManager,
    ) -> None:
        self._viewmodel = viewmodel
        self._resource_manager = resource_manager
        self._background_image: Optional[InteractiveImage] = None
        self._current_image: Optional[Image.Image] = None
        self._current_sections = self._viewmodel.get_all_sections()
        self._new_sections = self._current_sections
        self._introduce_to_viewmodel()
        self._current_section: Section | None = None
        self._current_point: Circle | None = None
        self._new_point: Circle | None = None
        self.add_preview_image()
        self._new_section_points: list[Circle] = []
        self._new_section = False
        self._new_area_section = False
        self._sections: SectionResource = SectionResource({})
        self._flows: LineResources = LineResources({})
        self._circles: CircleResources = CircleResources({})

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_canvas(self)
        self._viewmodel.set_canvas(self)
        self._viewmodel.set_treeview_files(self)

    def add_preview_image(self) -> None:
        self._current_image = self._resource_manager.get_image(CanvasKeys.IMAGE_DEFAULT)

    def build(self) -> Self:
        self._background_image = ui.interactive_image(
            "", on_mouse=self._on_pointer_down, events=[CLICK]
        )
        self._background_image.on(
            "svg:pointerdown", lambda e: self.on_svg_pointer_down(e.args)
        )
        self._background_image.on(
            "svg:pointermove", lambda e: self.on_svg_pointer_move(e.args)
        )
        self._background_image.on(
            "svg:pointerup", lambda e: self.on_svg_pointer_up(e.args)
        )

        self._change_image()
        ui.keyboard(on_key=self.handle_key)
        self.load_sections()
        return self

    async def handle_key(self, e: KeyEventArguments) -> None:
        if e.key == self._resource_manager.get_hotkey(HotKeys.SAVE_SECTION_HOTKEY):
            if self._new_section:
                coordinates = [circle.to_tuple() for circle in self._new_section_points]
                self.__reset_editor()
                await self._viewmodel.add_new_section(
                    coordinates=coordinates,
                    is_area_section=self._new_area_section,
                    get_metadata=self.__get_metadata,
                )
            elif self._current_section:
                metadata = self._current_section.to_dict()
                coordinates = self._current_section_geometry()
                self.__reset_editor()
                self._viewmodel.update_section_coordinates(metadata, coordinates)
        if e.key == self._resource_manager.get_hotkey(
            HotKeys.CANCEL_SECTION_GEOMETRY_HOTKEY
        ):
            self._viewmodel.cancel_action()
            self._viewmodel.refresh_items_on_canvas()

    def _current_section_geometry(self) -> list[tuple[int, int]]:
        if self._current_section is None:
            return []
        circles = self._circles.by_section.get(self._current_section.id.id, {})
        return circle_to_coordinates(circles.values())

    def __reset_editor(self) -> None:
        self._new_section = False
        self._current_section = None
        self._current_point = None
        self._new_section_points = []

    async def __get_metadata(self) -> dict:
        title = self._resource_manager.get(
            CanvasKeys.LABEL_EDIT_SECTION
            if self._current_section
            else CanvasKeys.LABEL_ADD_SECTION
        )
        return await self._viewmodel.get_section_metadata(
            title=title, initial_position=(0, 0)
        )

    def draw_all(self) -> None:
        if self._background_image:
            self._background_image.content = self._edit_geometry()
            self._background_image.content += self._sections.to_svg()
            self._background_image.content += self._flows.to_svg()
            self._background_image.content += self._circles.to_svg()
            if self._current_point:
                self._background_image.content += self._current_point.to_svg()
            if self._new_point:
                self._background_image.content += self._new_point.to_svg()
            self.draw_new_section()

    def draw_new_section(self) -> None:
        for point in self._new_section_points:
            if self._background_image:
                self._background_image.content += point.to_svg()
        if len(self._new_section_points) >= 2:
            coordinates = circle_to_coordinates(self._new_section_points)
            if self._new_area_section:
                coordinates.append(coordinates[0])
            line = Polyline(id=NEW_SECTION_ID, points=coordinates, color=EDIT_COLOR)
            if self._background_image:
                self._background_image.content += line.to_svg()

    def _edit_geometry(self) -> str:
        if self._current_section is None:
            return ""
        section_id = f"{self._current_section.id.id}-edit"
        return Polyline(
            id=section_id, points=self._current_section_geometry(), color=EDIT_COLOR
        ).to_svg()

    def _on_pointer_down(self, e: events.MouseEventArguments) -> None:
        if self._new_section:
            self._new_section_points.append(
                Circle(
                    x=round(e.image_x),
                    y=round(e.image_y),
                    pointer_event=POINTER_EVENT_ALL,
                    cursor=CURSOR,
                    fill=EDIT_COLOR,
                    id=f"new_point-{len(self._new_section_points)}",
                )
            )
            self.draw_all()

    def on_svg_pointer_down(self, e: dict) -> None:
        if self._new_section:
            pass
        elif self._current_section:
            self._current_point = create_moving_circle(e, fill=EDIT_COLOR)
            self.draw_all()

    def on_svg_pointer_move(self, e: dict) -> None:
        if self._current_section and self._current_point:
            self._current_point = create_moving_circle(e, fill=EDIT_COLOR)
            self._circles.add(self._current_section.id.id, self._current_point)
            self.draw_all()

    def on_svg_pointer_up(self, e: dict) -> None:
        if self._new_section:
            pass
        elif self._current_section and self._current_point:
            self._circles.add(
                self._current_section.id.id, create_circle(e, fill=EDIT_COLOR)
            )
            self._current_point = None
            self.draw_all()

    def update_background(self, image: TrackImage) -> None:
        self._current_image = image.as_image()
        self._change_image()

    def _change_image(self) -> None:
        if self._current_image and self._background_image:
            self._background_image.set_source(self._current_image)
        else:
            self.clear_image()

    def clear_image(self) -> None:
        if self._background_image:
            self._background_image.set_source("")

    def load_sections(self) -> None:
        self._viewmodel.refresh_items_on_canvas()

    def draw_current_point(self) -> None:
        if self._background_image:
            if self._current_point:
                self._background_image.content += self._current_point.to_svg()

    def draw_section(
        self,
        id: str,
        coordinates: list[tuple[int, int]],
        is_selected_section: bool,
        is_area_section: bool = False,
        highlighted_knob_index: int | None = None,
        highlighted_knob_style: dict | None = None,
        text: str | None = None,
        tags: list[str] | None = None,
    ) -> None:
        list_of_circle = []
        color = NORMAL_COLOR
        pointer_event = POINTER_EVENT_NONE
        if is_selected_section:
            color = SELECTED_COLOR
            pointer_event = POINTER_EVENT_ALL
        for index, coordinate in enumerate(coordinates):
            x = coordinate[0]
            y = coordinate[1]
            list_of_circle.append(
                Circle(
                    x=x,
                    y=y,
                    id=f"{id}-{index}",
                    fill=color,
                    pointer_event=pointer_event,
                )
            )
        for circle in list_of_circle:
            self._circles.add(id, circle)
        polyline = Polyline(id, coordinates, color=color)
        self._sections.add(id, polyline)
        if self._current_point:
            self.draw_current_point()
        self.draw_all()

    def start_section_geometry_editor(
        self,
        section: Section,
        hovered_knob_style: dict | None = None,
        is_area_section: bool = False,
    ) -> None:
        self._current_section = section
        self.draw_all()

    def draw_arrow(
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
        new_line = Line(
            id=f"arrow-{start_section.id}-{end_section.id}",
            x1=int(start_x),
            x2=int(end_x),
            y1=int(start_y),
            y2=int(end_y),
            stroke=NORMAL_COLOR,
        )
        self._flows.add(new_line)
        self.draw_all()

    def delete_element(self, tag_or_id: str) -> None:
        if tag_or_id == TAG_SELECTED_SECTION:
            return
        self._flows.clear()
        self._sections.clear()
        self._circles.clear()

    def start_section_builder(
        self,
        is_area_section: bool = False,
        section: Optional[Section] = None,
    ) -> None:
        self._new_section = True
        self._new_area_section = is_area_section

    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        return 0, 0

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        pass

    def disable(self) -> None:
        pass

    def enable(self) -> None:
        pass

    def update_items(self) -> None:
        pass

    def update_selected_items(self, item_ids: list[str]) -> None:
        pass

    def introduce_to_viewmodel(self) -> None:
        pass
