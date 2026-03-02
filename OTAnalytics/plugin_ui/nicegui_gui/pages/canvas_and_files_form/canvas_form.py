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
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.midpoint_circle import MidpointCircle
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line import Line
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line_resources import LineResources
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polyline import Polyline
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.section_resources import (
    SectionResource,
)
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

NORMAL_COLOR = "green"
SELECTED_COLOR = "red"
EDIT_COLOR = "orange"
MOVING_COLOR = "blue"
MOVING_STROKE_WIDTH = 400
MOVING_STROKE_OPACITY = 0.0
MARKER_INTERACTIVE_IMAGE = "marker-interactive-image"

CLICK = "click"
POINTER_EVENT_ALL = "all"
POINTER_EVENT_NONE = ""
IMAGE_X = "image_x"
IMAGE_Y = "image_y"
ELEMENT_ID = "element_id"

CURSOR = "pointer"
NEW_SECTION_ID = "new-section-id"
MIDPOINT_ID_EDIT_PREFIX = "mid"
MIDPOINT_ID_NEW_PREFIX = "new-mid"


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


def compute_midpoints(
    points: list[tuple[int, int]], id_prefix: str
) -> list[MidpointCircle]:
    """Return one MidpointCircle per consecutive pair of points."""
    result = []
    for i in range(len(points) - 1):
        x = (points[i][0] + points[i + 1][0]) // 2
        y = (points[i][1] + points[i + 1][1]) // 2
        result.append(MidpointCircle(id=f"{id_prefix}-{i}", x=x, y=y))
    return result


def insert_circle_at_index(
    circles: dict[str, Circle], idx: int, circle: Circle
) -> dict[str, Circle]:
    """Return a new ordered dict with circle inserted at position idx."""
    items = list(circles.items())
    items.insert(idx, (circle.id, circle))
    return dict(items)


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
        self._new_section_dragging_idx: int | None = None
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
        self._background_image.props(f"{TEST_ID}={MARKER_INTERACTIVE_IMAGE}")
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
                await self._save_new_section()
            elif self._current_section:
                self._save_edit_section()
        if e.key == self._resource_manager.get_hotkey(
            HotKeys.CANCEL_SECTION_GEOMETRY_HOTKEY
        ):
            self._cancel_action()

    async def _save_new_section(self) -> None:
        """Save a new section with the current points."""
        coordinates = [circle.to_tuple() for circle in self._new_section_points]
        self.__reset_editor()
        await self._viewmodel.add_new_section(
            coordinates=coordinates,
            is_area_section=self._new_area_section,
            get_metadata=self.__get_metadata,
        )

    def _save_edit_section(self) -> None:
        """Save changes to an existing section."""
        if self._current_section is None:
            return
        metadata = self._current_section.to_dict()
        coordinates = self._current_section_geometry()
        self.__reset_editor()
        self._viewmodel.update_section_coordinates(metadata, coordinates)

    def _cancel_action(self) -> None:
        """Cancel the current action and refresh the canvas."""
        self.__reset_editor()
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
        self._new_section_dragging_idx = None

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
            self._background_image.content += self._midpoints_svg_for_section()
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
        if self._background_image:
            self._background_image.content += self._midpoints_svg_for_new_section()

    def _edit_geometry(self) -> str:
        if self._current_section is None:
            return ""
        section_id = f"{self._current_section.id.id}-edit"
        return Polyline(
            id=section_id, points=self._current_section_geometry(), color=EDIT_COLOR
        ).to_svg()

    def _midpoints_svg_for_section(self) -> str:
        """Return SVG for midpoint affordances in edit mode."""
        if self._current_section is None:
            return ""
        section_id = self._current_section.id.id
        circles = self._circles.by_section.get(section_id, {})
        points = circle_to_coordinates(circles.values())
        return "".join(
            mc.to_svg()
            for mc in compute_midpoints(
                points, f"{MIDPOINT_ID_EDIT_PREFIX}-{section_id}"
            )
        )

    def _midpoints_svg_for_new_section(self) -> str:
        """Return SVG for midpoint affordances when building a new section."""
        if len(self._new_section_points) < 2:
            return ""
        points = circle_to_coordinates(self._new_section_points)
        return "".join(
            mc.to_svg()
            for mc in compute_midpoints(points, MIDPOINT_ID_NEW_PREFIX)
        )

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
        element_id = e.get(ELEMENT_ID, "")
        if self._current_section and element_id.startswith(
            f"{MIDPOINT_ID_EDIT_PREFIX}-{self._current_section.id.id}-"
        ):
            self._insert_midpoint_in_edit_mode(e, element_id)
        elif self._new_section and element_id.startswith(
            f"{MIDPOINT_ID_NEW_PREFIX}-"
        ):
            self._insert_midpoint_in_new_section_mode(element_id)
        elif self._new_section:
            pass
        elif self._current_section:
            self._current_point = create_moving_circle(e, fill=EDIT_COLOR)
            self.draw_all()

    def _insert_midpoint_in_edit_mode(self, e: dict, element_id: str) -> None:
        """Insert a new control point at segment midpoint and start dragging it."""
        section_id = self._current_section.id.id  # type: ignore[union-attr]
        # ID format: "mid-{section_id}-{segment_idx}"
        segment_idx = int(element_id.rsplit("-", 1)[-1])
        circles = self._circles.by_section.get(section_id, {})
        points = circle_to_coordinates(circles.values())
        mid_x = (points[segment_idx][0] + points[segment_idx + 1][0]) // 2
        mid_y = (points[segment_idx][1] + points[segment_idx + 1][1]) // 2
        new_id = f"{section_id}-inserted-{segment_idx}"
        new_circle = Circle(
            id=new_id,
            x=mid_x,
            y=mid_y,
            fill=EDIT_COLOR,
            pointer_event=POINTER_EVENT_ALL,
            stroke=MOVING_COLOR,
            stroke_width=MOVING_STROKE_WIDTH,
            stroke_opacity=MOVING_STROKE_OPACITY,
        )
        updated = insert_circle_at_index(circles, segment_idx + 1, new_circle)
        self._circles.by_section[section_id] = updated
        self._circles.circles.update(updated)
        self._current_point = new_circle
        self.draw_all()

    def _insert_midpoint_in_new_section_mode(self, element_id: str) -> None:
        """Insert point at segment midpoint in new-section creation mode and start drag."""
        # ID format: "new-mid-{segment_idx}"
        segment_idx = int(element_id.rsplit("-", 1)[-1])
        p0 = self._new_section_points[segment_idx]
        p1 = self._new_section_points[segment_idx + 1]
        mid_x = (p0.x + p1.x) // 2
        mid_y = (p0.y + p1.y) // 2
        insert_idx = segment_idx + 1
        new_circle = Circle(
            id=f"new_point-inserted-{segment_idx}",
            x=mid_x,
            y=mid_y,
            fill=EDIT_COLOR,
            pointer_event=POINTER_EVENT_ALL,
            cursor=CURSOR,
        )
        self._new_section_points.insert(insert_idx, new_circle)
        self._new_section_dragging_idx = insert_idx
        self.draw_all()

    def on_svg_pointer_move(self, e: dict) -> None:
        if self._new_section_dragging_idx is not None:
            idx = self._new_section_dragging_idx
            self._new_section_points[idx] = Circle(
                id=self._new_section_points[idx].id,
                x=round(e[IMAGE_X]),
                y=round(e[IMAGE_Y]),
                fill=EDIT_COLOR,
                pointer_event=POINTER_EVENT_ALL,
                cursor=CURSOR,
            )
            self.draw_all()
        elif self._current_section and self._current_point:
            self._current_point = create_moving_circle(e, fill=EDIT_COLOR)
            self._circles.add(self._current_section.id.id, self._current_point)
            self.draw_all()

    def on_svg_pointer_up(self, e: dict) -> None:
        if self._new_section_dragging_idx is not None:
            idx = self._new_section_dragging_idx
            self._new_section_points[idx] = Circle(
                id=self._new_section_points[idx].id,
                x=round(e[IMAGE_X]),
                y=round(e[IMAGE_Y]),
                fill=EDIT_COLOR,
                pointer_event=POINTER_EVENT_ALL,
                cursor=CURSOR,
            )
            self._new_section_dragging_idx = None
            self.draw_all()
        elif self._new_section:
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
