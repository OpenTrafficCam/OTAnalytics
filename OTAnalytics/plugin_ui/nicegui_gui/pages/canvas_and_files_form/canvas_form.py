from typing import Any, Final, Iterable, Optional, Self

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
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.arrow import Arrow
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.circle import Circle
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.circle_resources import (
    CircleResources,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line_resources import LineResources
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polygon import Polygon
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polyline import Polyline
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.section_resources import (
    SectionResource,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.text import Text
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.section_geometry import (  # noqa
    Point,
    close_area,
    closest_knob_index,
    delete_knob,
    has_enough_knobs,
    insert_knob,
    minimum_knob_count,
    open_area,
    shift_knob_backward,
    shift_knob_forward,
)
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

NORMAL_COLOR = "green"
SELECTED_COLOR = "red"
EDIT_COLOR = "orange"
MOVING_COLOR = "blue"
HOVERED_KNOB_COLOR = "yellow"
MOVING_STROKE_WIDTH = 400
MOVING_STROKE_OPACITY = 0.0
MARKER_INTERACTIVE_IMAGE = "marker-interactive-image"

CLICK = "click"
MOUSE_MOVE = "mousemove"
MOUSE_UP = "mouseup"
CONTEXT_MENU = "contextmenu.prevent"
PASSIVE_MOUSE_EVENTS = [CLICK]
EDITOR_MOUSE_EVENTS = [CLICK, MOUSE_MOVE, MOUSE_UP]
EVENTS_PROP = "events"
NOTIFICATION_TYPE_WARNING: Final = "warning"
POINTER_EVENT_ALL = "all"
POINTER_EVENT_NONE = ""
IMAGE_X = "image_x"
IMAGE_Y = "image_y"
ELEMENT_ID = "element_id"

CURSOR = "pointer"
CURSOR_MOVE = "move"
NEW_SECTION_ID = "new-section-id"
EDIT_KNOB_ID_PREFIX = "edit-knob-"
KNOB_RADIUS = 6
HIGHLIGHTED_KNOB_RADIUS = 8
HIGHLIGHTED_KNOB_STROKE_WIDTH = 3
KNOB_CATCH_RADIUS = 15
SECTION_TEXT_OFFSET_Y = -12

# Keys of the arrow style, named like the options of the customtkinter canvas
ARROW_STYLE_COLOR = "fill"
ARROW_STYLE_WIDTH = "width"
ARROW_STYLE_DASH = "dash"
DEFAULT_ARROW_STYLE: dict = {ARROW_STYLE_COLOR: NORMAL_COLOR, ARROW_STYLE_WIDTH: 2}


def circle_to_coordinates(circles: Iterable[Circle]) -> list[tuple[int, int]]:
    return [circle.to_tuple() for circle in circles]


def create_section_shape(
    id: str, coordinates: list[Point], color: str, is_area_section: bool
) -> Polyline | Polygon:
    """Area sections are drawn closed and filled, line sections as polyline."""
    if is_area_section:
        return Polygon(id=id, points=open_area(coordinates, True), color=color)
    return Polyline(id=id, points=coordinates, color=color)


def to_point(x: float, y: float) -> Point:
    return round(x), round(y)


def svg_event_to_point(e: dict) -> Point:
    return to_point(e[IMAGE_X], e[IMAGE_Y])


def knob_index_from_element_id(element_id: str | None) -> int | None:
    if not element_id or not element_id.startswith(EDIT_KNOB_ID_PREFIX):
        return None
    try:
        return int(element_id.removeprefix(EDIT_KNOB_ID_PREFIX))
    except ValueError:
        return None


def create_knob(
    index: int, point: Point, is_hovered: bool = False, is_selected: bool = False
) -> Circle:
    """Create the circle of a knob of the section geometry editor.

    A selected knob gets a large transparent stroke. Thereby, the svg keeps
    receiving pointer events while the knob is moved.
    """
    knob = Circle(
        id=f"{EDIT_KNOB_ID_PREFIX}{index}",
        x=point[0],
        y=point[1],
        fill=EDIT_COLOR,
        pointer_event=POINTER_EVENT_ALL,
        radius=KNOB_RADIUS,
        stroke=EDIT_COLOR,
        stroke_width=0,
        cursor=CURSOR_MOVE,
    )
    if is_selected:
        knob.fill = MOVING_COLOR
        knob.radius = HIGHLIGHTED_KNOB_RADIUS
        knob.stroke = MOVING_COLOR
        knob.stroke_width = MOVING_STROKE_WIDTH
        knob.stroke_opacity = MOVING_STROKE_OPACITY
    elif is_hovered:
        knob.radius = HIGHLIGHTED_KNOB_RADIUS
        knob.stroke = HOVERED_KNOB_COLOR
        knob.stroke_width = HIGHLIGHTED_KNOB_STROKE_WIDTH
        knob.stroke_opacity = 1.0
    return knob


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
        self._edit_is_area_section = False
        self._edit_coordinates: list[Point] = []
        self._edit_temporary: list[Point] = []
        self._hovered_knob_index: int | None = None
        self._selected_knob_index: int | None = None
        self._dragging = False
        self._drop_on_release = False
        self._knob_moved = False
        self._mouse_position: Point | None = None
        self._enabled = True
        self.add_preview_image()
        self._new_section_points: list[Circle] = []
        self._preview_point: Point | None = None
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
            "", on_mouse=self.on_mouse, events=list(PASSIVE_MOUSE_EVENTS)
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
        self._background_image.on(CONTEXT_MENU, self.on_right_click)

        self._change_image()
        ui.keyboard(on_key=self.handle_key)
        self.load_sections()
        return self

    def _is_editor_active(self) -> bool:
        return self._new_section or self._current_section is not None

    def _accepts_input(self) -> bool:
        return self._enabled and self._is_editor_active()

    def _is_hotkey(self, e: KeyEventArguments, hotkey: HotKeys) -> bool:
        return e.key == self._resource_manager.get_hotkey(hotkey)

    async def handle_key(self, e: KeyEventArguments) -> None:
        """Handle key presses. Keys are only evaluated while an editor is active.

        This prevents key presses in other parts of the page from being handled by
        the canvas.
        """
        if not self._accepts_input() or not e.action.keydown:
            return
        if self._is_hotkey(e, HotKeys.SAVE_SECTION_HOTKEY):
            await self._finish_editor()
        elif self._is_hotkey(e, HotKeys.CANCEL_SECTION_GEOMETRY_HOTKEY):
            self._on_cancel_key()
        elif self._current_section is not None:
            self._handle_geometry_editor_key(e)

    def _on_cancel_key(self) -> None:
        if self._current_section is not None and self._selected_knob_index is not None:
            self._deselect_knob(revert=True)
            self.draw_all()
        else:
            self._cancel_action()

    def _handle_geometry_editor_key(self, e: KeyEventArguments) -> None:
        if self._is_hotkey(e, HotKeys.ADD_KNOB_HOTKEY):
            self._add_knob()
        elif self._is_hotkey(e, HotKeys.DELETE_KNOB_HOTKEY) or self._is_hotkey(
            e, HotKeys.DELETE_KNOB_ALTERNATIVE_HOTKEY
        ):
            self._delete_selected_knob()
        elif self._is_hotkey(e, HotKeys.SHIFT_KNOB_BACKWARD_HOTKEY):
            self._shift_selected_knob(forward=False)
        elif self._is_hotkey(e, HotKeys.SHIFT_KNOB_FORWARD_HOTKEY):
            self._shift_selected_knob(forward=True)

    def _add_knob(self) -> None:
        """Insert a knob at the mouse position between the closest knobs.

        The new knob is selected and follows the mouse until it is placed by a click.
        """
        if self._selected_knob_index is not None or self._mouse_position is None:
            return
        self._edit_temporary, self._selected_knob_index = insert_knob(
            self._edit_temporary, self._mouse_position, self._edit_is_area_section
        )
        self._hovered_knob_index = None
        self._dragging = False
        self.draw_all()

    def _delete_selected_knob(self) -> None:
        if self._selected_knob_index is None:
            return
        self._edit_temporary = delete_knob(
            self._edit_temporary,
            self._selected_knob_index,
            self._edit_is_area_section,
        )
        self._commit_edit()
        self._deselect_knob(revert=False)
        self.draw_all()

    def _shift_selected_knob(self, forward: bool) -> None:
        if self._selected_knob_index is None:
            return
        shift = shift_knob_forward if forward else shift_knob_backward
        self._edit_temporary, self._selected_knob_index = shift(
            self._edit_temporary,
            self._selected_knob_index,
            self._edit_is_area_section,
        )
        self.draw_all()

    def _commit_edit(self) -> None:
        self._edit_coordinates = list(self._edit_temporary)

    def _deselect_knob(self, revert: bool) -> None:
        if revert:
            self._edit_temporary = list(self._edit_coordinates)
        self._selected_knob_index = None
        self._dragging = False
        self._drop_on_release = False
        self._knob_moved = False

    async def on_right_click(self, _: Any = None) -> None:
        """Finish the active editor like the save hotkey does."""
        if self._accepts_input():
            await self._finish_editor()

    async def _finish_editor(self) -> None:
        if self._new_section:
            await self._save_new_section()
        elif self._current_section:
            self._save_edit_section()

    async def _save_new_section(self) -> None:
        """Save a new section with the current points.

        The section is only saved if enough points have been added. Otherwise, the
        user is notified and can continue adding points.
        """
        coordinates = [circle.to_tuple() for circle in self._new_section_points]
        is_area_section = self._new_area_section
        if not has_enough_knobs(coordinates, is_area_section):
            self._notify_not_enough_points(is_area_section)
            return
        self.__reset_editor()
        await self._viewmodel.add_new_section(
            coordinates=close_area(coordinates, is_area_section),
            is_area_section=is_area_section,
            get_metadata=self.__get_metadata,
        )

    def _notify_not_enough_points(self, is_area_section: bool) -> None:
        message = self._resource_manager.get(CanvasKeys.MESSAGE_NOT_ENOUGH_POINTS)
        ui.notify(
            message.format(count=minimum_knob_count(is_area_section)),
            type=NOTIFICATION_TYPE_WARNING,
        )

    def _save_edit_section(self) -> None:
        """Save changes to an existing section."""
        if self._current_section is None:
            return
        metadata = self._current_section.to_dict()
        coordinates = close_area(self._edit_temporary, self._edit_is_area_section)
        self.__reset_editor()
        self._viewmodel.update_section_coordinates(metadata, coordinates)

    def _cancel_action(self) -> None:
        """Cancel the current action and refresh the canvas."""
        self.__reset_editor()
        self._viewmodel.cancel_action()
        self._viewmodel.refresh_items_on_canvas()

    def __reset_editor(self) -> None:
        self._new_section = False
        self._current_section = None
        self._new_section_points = []
        self._preview_point = None
        self._reset_geometry_editor()
        self._update_mouse_events()

    def _reset_geometry_editor(self) -> None:
        self._edit_coordinates = []
        self._edit_temporary = []
        self._hovered_knob_index = None
        self._mouse_position = None
        self._deselect_knob(revert=False)

    def _update_mouse_events(self) -> None:
        """Subscribe to mouse movements only while an editor is active.

        This avoids sending every mouse movement to the server if nobody needs it.
        """
        if self._background_image is None:
            return
        events = (
            EDITOR_MOUSE_EVENTS if self._is_editor_active() else PASSIVE_MOUSE_EVENTS
        )
        self._background_image._props[EVENTS_PROP] = list(events)
        self._background_image.update()

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
            self._background_image.content = self._sections.to_svg()
            self._background_image.content += self._flows.to_svg()
            self._background_image.content += self._circles.to_svg()
            self._background_image.content += self._edit_geometry()
            self.draw_new_section()

    def draw_new_section(self) -> None:
        if not self._background_image:
            return
        coordinates = circle_to_coordinates(self._new_section_points)
        if coordinates and self._preview_point:
            coordinates.append(self._preview_point)
        if len(coordinates) >= 2:
            shape = create_section_shape(
                NEW_SECTION_ID, coordinates, EDIT_COLOR, self._new_area_section
            )
            self._background_image.content += shape.to_svg()
        for point in self._new_section_points:
            self._background_image.content += point.to_svg()

    def _edit_geometry(self) -> str:
        if self._current_section is None:
            return ""
        section_id = f"{self._current_section.id.id}-edit"
        svg = create_section_shape(
            section_id, self._edit_temporary, EDIT_COLOR, self._edit_is_area_section
        ).to_svg()
        for index, point in enumerate(self._edit_temporary):
            knob = create_knob(
                index,
                point,
                is_hovered=index == self._hovered_knob_index,
                is_selected=index == self._selected_knob_index,
            )
            svg += knob.to_svg()
        return svg

    def on_mouse(self, e: events.MouseEventArguments) -> None:
        """Dispatch mouse events of the interactive image."""
        if not self._accepts_input():
            return
        point = to_point(e.image_x, e.image_y)
        if e.type == MOUSE_MOVE:
            self._on_move(point)
        elif e.type == MOUSE_UP:
            self._on_release(point)
        elif e.type == CLICK:
            if self._current_section is not None:
                self._on_canvas_click(point)
            else:
                self._on_pointer_down(e)

    def _on_move(self, point: Point) -> None:
        if self._new_section:
            self._preview_point = point
            self.draw_all()
        elif self._current_section is not None:
            self._mouse_position = point
            if self._selected_knob_index is not None:
                self._move_selected_knob(point)
            else:
                self._hover_knob(point)

    def _move_selected_knob(self, point: Point) -> None:
        if self._selected_knob_index is None:
            return
        self._edit_temporary[self._selected_knob_index] = point
        if self._dragging:
            self._knob_moved = True
        self.draw_all()

    def _hover_knob(self, point: Point) -> None:
        hovered = closest_knob_index(self._edit_temporary, point, KNOB_CATCH_RADIUS)
        if hovered != self._hovered_knob_index:
            self._hovered_knob_index = hovered
            self.draw_all()

    def _on_release(self, point: Point) -> None:
        """Place the selected knob if it was dragged or picked up before."""
        if self._current_section is None or not self._dragging:
            return
        self._dragging = False
        if self._selected_knob_index is None:
            return
        if self._knob_moved or self._drop_on_release:
            self._place_selected_knob(point)
        self.draw_all()

    def _on_canvas_click(self, point: Point) -> None:
        if self._selected_knob_index is not None and not self._dragging:
            self._place_selected_knob(point)
            self.draw_all()

    def _place_selected_knob(self, point: Point) -> None:
        index = self._selected_knob_index
        if index is None:
            return
        self._edit_temporary[index] = point
        self._commit_edit()
        self._deselect_knob(revert=False)
        self._hovered_knob_index = index

    def _on_pointer_down(self, e: events.MouseEventArguments) -> None:
        if self._new_section:
            self._new_section_points.append(
                Circle(
                    x=round(e.image_x),
                    y=round(e.image_y),
                    pointer_event=POINTER_EVENT_NONE,
                    cursor=CURSOR,
                    fill=EDIT_COLOR,
                    id=f"new_point-{len(self._new_section_points)}",
                )
            )
            self.draw_all()

    def on_svg_pointer_down(self, e: dict) -> None:
        """Select a knob of the edited section or pick up the selected knob."""
        if self._current_section is None or not self._enabled:
            return
        point = svg_event_to_point(e)
        self._mouse_position = point
        if self._selected_knob_index is None:
            index = knob_index_from_element_id(e.get(ELEMENT_ID))
            if index is None:
                index = closest_knob_index(
                    self._edit_temporary, point, KNOB_CATCH_RADIUS
                )
            if index is None:
                return
            self._selected_knob_index = index
            self._drop_on_release = False
        else:
            self._drop_on_release = True
        self._dragging = True
        self._knob_moved = False
        self.draw_all()

    def on_svg_pointer_move(self, e: dict) -> None:
        if self._accepts_input():
            self._on_move(svg_event_to_point(e))

    def on_svg_pointer_up(self, e: dict) -> None:
        if self._accepts_input():
            self._on_release(svg_event_to_point(e))

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
        knobs = open_area(coordinates, is_area_section)
        for index, coordinate in enumerate(knobs):
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
        self._sections.add(
            id, create_section_shape(id, coordinates, color, is_area_section)
        )
        if text is not None and coordinates:
            x, y = coordinates[0]
            self._sections.add_text(
                id,
                Text(
                    id=f"{id}-text",
                    x=x,
                    y=y + SECTION_TEXT_OFFSET_Y,
                    text=text,
                    color=color,
                ),
            )
        self.draw_all()

    def start_section_geometry_editor(
        self,
        section: Section,
        hovered_knob_style: dict | None = None,
        is_area_section: bool = False,
    ) -> None:
        self._new_section = False
        self._new_section_points = []
        self._preview_point = None
        self._reset_geometry_editor()
        self._enabled = True
        self._current_section = section
        self._edit_is_area_section = is_area_section
        coordinates = [
            to_point(coordinate.x, coordinate.y)
            for coordinate in section.get_coordinates()
        ]
        self._edit_coordinates = open_area(coordinates, is_area_section)
        self._edit_temporary = list(self._edit_coordinates)
        self._update_mouse_events()
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
        style = {**DEFAULT_ARROW_STYLE, **(arrow_style or {})}
        dash = style.get(ARROW_STYLE_DASH)
        arrow = Arrow(
            id=f"arrow-{start_section.id}-{end_section.id}",
            x1=int(start_x),
            x2=int(end_x),
            y1=int(start_y),
            y2=int(end_y),
            color=style[ARROW_STYLE_COLOR],
            width=style[ARROW_STYLE_WIDTH],
            dash=tuple(dash) if dash else None,
        )
        self._flows.add(arrow)
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
        self._enabled = True
        self._current_section = None
        self._reset_geometry_editor()
        self._new_section = True
        self._new_area_section = is_area_section
        self._new_section_points = []
        self._preview_point = None
        self._update_mouse_events()
        self.draw_all()

    def get_position(self, offset: tuple[float, float] = (0.5, 0.5)) -> tuple[int, int]:
        return 0, 0

    def _notify_viewmodel_about_selected_item_ids(self, ids: list[str]) -> None:
        pass

    def disable(self) -> None:
        """Ignore canvas input while an action is running.

        An editor started by the running action enables the canvas again, because
        the editor is part of this action.
        """
        self._enabled = False

    def enable(self) -> None:
        self._enabled = True

    def update_items(self) -> None:
        pass

    def update_selected_items(self, item_ids: list[str]) -> None:
        pass

    def introduce_to_viewmodel(self) -> None:
        pass
