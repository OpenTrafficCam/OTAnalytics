import time
from html import escape
from typing import Any, Final, Iterable, Optional, Self

from nicegui import events, ui
from nicegui.elements.interactive_image import InteractiveImage, InteractiveImageLayer
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
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.action_pill import (
    CANCEL_SUFFIX,
    FINISH_SUFFIX,
    HEIGHT,
    WIDTH,
    ActionPill,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.arrow import Arrow
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.circle import Circle
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.knob import (
    EDIT_KNOB_ID_PREFIX,
    Knob,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line import Line
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line_resources import LineResources
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.midpoint_circle import MidpointCircle
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polyline import Polyline
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import dot
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.section import SectionShape
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.section_resources import (
    SectionResource,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.shift_ring import (
    BACKWARD_SUFFIX,
    FORWARD_SUFFIX,
    ShiftRing,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.section_geometry import (  # noqa
    Point,
    close_area,
    closest_knob_index,
    delete_knob,
    has_enough_knobs,
    insert_knob,
    insert_knob_at_segment,
    minimum_knob_count,
    open_area,
    ring_half_at,
    segment_midpoints,
    shift_knob_backward,
    shift_knob_forward,
    shift_target_index,
)
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID

MARKER_INTERACTIVE_IMAGE = "marker-interactive-image"

CLICK = "click"
MOUSE_MOVE = "mousemove"
MOUSE_UP = "mouseup"
MOUSE_DOWN = "mousedown"
CONTEXT_MENU = "contextmenu.prevent"
PASSIVE_MOUSE_EVENTS = [CLICK]
EDITOR_MOUSE_EVENTS = [CLICK, MOUSE_DOWN, MOUSE_MOVE, MOUSE_UP]
EVENTS_PROP = "events"
SIZE_PROP = "size"
UPDATE_VIEWBOX = "updateViewbox"
RELEASE_FOCUS = "document.activeElement?.blur()"
NOTIFICATION_TYPE_WARNING: Final = "warning"
IMAGE_X = "image_x"
IMAGE_Y = "image_y"
ELEMENT_ID = "element_id"

NEW_SECTION_ID = "new-section-id"
RUBBER_ID = "rubber"
KNOB_CATCH_RADIUS = 15
EDIT_MIDPOINT_ID_PREFIX = "edit-mid-"
EDIT_SHIFT_ID: Final = "edit-shift"
EDIT_ACTION_ID: Final = "edit-action"
# Elements of the editor, which the browser reports to the server
EDITOR_ELEMENT_PREFIXES: Final = (
    EDIT_KNOB_ID_PREFIX,
    EDIT_MIDPOINT_ID_PREFIX,
    f"{EDIT_SHIFT_ID}-",
    f"{EDIT_ACTION_ID}-",
)
# Sizes of the affordances in screen pixels, see otanalytics.css
SHIFT_RING_INNER_RADIUS: Final = 18
SHIFT_RING_OUTER_RADIUS: Final = 42
SHIFT_RING_IDLE_SECONDS: Final = 0.3
SHIFT_RING_POLL_SECONDS: Final = 0.1
# Distance of the pill's center below its knob: the knob's halo (20), a gap (2)
# and half the pill (16). Nothing else of the knob is drawn while the pill shows.
ACTION_PILL_OFFSET: Final = 38
SCALE_EVENT = "scalechange"

# Styled by otanalytics.css, see docs/otanalytics-overlay-spec.md
CANVAS_CLASS = "ota-canvas"
OVERLAY_CLASS = "ota-overlay"
FOCUS_CLASS = "ota-focus"
HINT_CLASS = "ota-hint"
GHOST_CLASS = "ota-ghost"
HINT_TEXT = "Drag points · + add · Del remove · Enter finish · Esc cancel"
NEW_LINE_SECTION_NAME = "New line section"
NEW_AREA_NAME = "New area"
# Items sized in screen pixels are scaled by --ota-s, the image pixels per
# screen pixel of the overlay.
# Recomputed when the overlay is resized or the image size changes. Installed
# once per svg, as it runs again on every reconnect.
SCALE_OBSERVER_JS = """
const svg = getHtmlElement({id})?.querySelector('svg');
if (svg && !svg.otaScale) {{
  svg.otaScale = () => {{
    if (svg.clientWidth > 0) {{
      const scale = svg.viewBox.baseVal.width / svg.clientWidth;
      svg.style.setProperty('--ota-s', scale);
      getHtmlElement({id}).dispatchEvent(
        new CustomEvent("scalechange", {{ detail: scale }})
      );
    }}
  }};
  new ResizeObserver(svg.otaScale).observe(svg);
  new MutationObserver(svg.otaScale).observe(svg, {{ attributeFilter: ['viewBox'] }});
  svg.otaScale();
}}
"""
# Only the elements of the editor need the svg pointer events. Dropping all others
# in the browser avoids sending every mouse movement over a section to the server.
EDITOR_EVENTS_ONLY_JS = (
    "(e) => { "
    f"if ({list(EDITOR_ELEMENT_PREFIXES)}.some("
    "(prefix) => e.element_id?.startsWith(prefix))) emit(e); }"
)


def circle_to_coordinates(circles: Iterable[Circle]) -> list[tuple[int, int]]:
    return [circle.to_tuple() for circle in circles]


def fit_into_workspace(width: int, height: int) -> str:
    """Style the image as large as the workspace allows, keeping its aspect ratio.

    The mouse positions are scaled by the size of the image element. Stretching
    or letterboxing the image inside its element would shift them, so the
    element itself takes the aspect ratio of the image. The workspace provides
    its size as a CSS container.
    """
    return (
        f"aspect-ratio: {width} / {height}; "
        f"width: min(100cqw, calc(100cqh * {width} / {height}))"
    )


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
    index: int,
    point: Point,
    is_hovered: bool = False,
    is_selected: bool = False,
    is_partner: bool = False,
    number: int | None = None,
) -> Knob:
    """Create a knob of the section geometry editor.

    A hovered or selected knob is active. A selected knob follows the mouse. The
    partner is the knob that swaps with the selected one in the shift preview.
    """
    return Knob(
        index=index,
        x=point[0],
        y=point[1],
        active=is_hovered or is_selected,
        moving=is_selected,
        partner=is_partner,
        number=number,
    )


def midpoint_index_from_element_id(element_id: str | None) -> int | None:
    if not element_id or not element_id.startswith(EDIT_MIDPOINT_ID_PREFIX):
        return None
    try:
        return int(element_id.removeprefix(EDIT_MIDPOINT_ID_PREFIX))
    except ValueError:
        return None


def hint_content(name: str) -> str:
    return f"<i></i><b>Editing {escape(name)}</b>{HINT_TEXT}"


class CanvasForm(AbstractCanvas, AbstractFrameCanvas, AbstractTreeviewInterface):
    def __init__(
        self,
        viewmodel: ViewModel,
        resource_manager: ResourceManager,
    ) -> None:
        self._viewmodel = viewmodel
        self._resource_manager = resource_manager
        self._background_image: Optional[InteractiveImage] = None
        self._overlay: Optional[InteractiveImageLayer] = None
        self._hint: Optional[ui.html] = None
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
        self._flows_outdated = False
        self._screen_scale = 1.0
        self._shift_anchor: Point | None = None
        self._shift_hovered_forward: bool | None = None
        self._last_knob_motion = 0.0
        self._last_placed_knob: Point | None = None
        # Whether the current press started on an editor element of the svg. The
        # image reports a click for such a press, too, which must be ignored.
        self._press_on_svg = False
        self._shift_ring_timer: ui.timer | None = None

    def _introduce_to_viewmodel(self) -> None:
        self._viewmodel.set_frame_canvas(self)
        self._viewmodel.set_canvas(self)
        self._viewmodel.set_treeview_files(self)

    def add_preview_image(self) -> None:
        self._current_image = self._resource_manager.get_image(CanvasKeys.IMAGE_DEFAULT)
        self._change_image()

    def build(self) -> Self:
        self._background_image = ui.interactive_image(
            "", on_mouse=self.on_mouse, events=list(PASSIVE_MOUSE_EVENTS)
        )
        self._background_image.props(f"{TEST_ID}={MARKER_INTERACTIVE_IMAGE}")
        self._background_image.classes(CANVAS_CLASS)
        # Sections are drawn on a layer, because every change of the image's own
        # content resends its whole background. Created before the background is
        # set, as the layer copies the image's source.
        self._overlay = self._background_image.add_layer()
        self._overlay.classes(OVERLAY_CLASS)
        self._overlay.on(
            "svg:pointerdown",
            lambda e: self.handle_svg_pointer_down(e.args),
            js_handler=EDITOR_EVENTS_ONLY_JS,
        )
        self._overlay.on(
            "svg:pointermove",
            lambda e: self.on_svg_pointer_move(e.args),
            js_handler=EDITOR_EVENTS_ONLY_JS,
        )
        self._overlay.on(
            "svg:pointerup",
            lambda e: self.on_svg_pointer_up(e.args),
            js_handler=EDITOR_EVENTS_ONLY_JS,
        )
        self._overlay.on(SCALE_EVENT, self._on_scale, args=["detail"])
        self._background_image.on(CONTEXT_MENU, self.on_right_click)
        with self._background_image:
            self._hint = ui.html()
            self._hint.classes(HINT_CLASS)
            self._hint.set_visibility(False)
        self._observe_scale()

        self._shift_ring_timer = ui.timer(
            SHIFT_RING_POLL_SECONDS, self._show_shift_ring_when_still, active=False
        )
        self._change_image()
        ui.keyboard(on_key=self.handle_key)
        self.load_sections()
        return self

    def _on_scale(self, e: events.GenericEventArguments) -> None:
        """Image pixels per screen pixel of the overlay, sent by the browser."""
        detail = e.args.get("detail") if isinstance(e.args, dict) else e.args
        if isinstance(detail, (int, float)) and detail > 0:
            self._screen_scale = float(detail)

    def _observe_scale(self) -> None:
        if self._overlay is None:
            return
        client = self._overlay.client
        script = SCALE_OBSERVER_JS.format(id=self._overlay.id)
        if client.has_socket_connection:
            client.run_javascript(script)
        else:
            client.on_connect(lambda: client.run_javascript(script))

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
        self._last_knob_motion = time.monotonic()
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
        self._update_editor_state()

    def _reset_geometry_editor(self) -> None:
        self._edit_coordinates = []
        self._edit_temporary = []
        self._hovered_knob_index = None
        self._mouse_position = None
        self._last_placed_knob = None
        self._deselect_knob(revert=False)

    def _update_editor_state(self) -> None:
        self._update_mouse_events()
        self._update_focus()

    def _update_focus(self) -> None:
        """Dim everything but the edited section and explain the editor's keys."""
        if self._overlay is not None:
            if self._is_editor_active():
                self._overlay.classes(add=FOCUS_CLASS)
            else:
                self._overlay.classes(remove=FOCUS_CLASS)
        if self._hint is not None:
            if self._is_editor_active():
                self._hint.set_content(hint_content(self._editor_name()))
            self._hint.set_visibility(self._is_editor_active())

    def _editor_name(self) -> str:
        if self._current_section is not None:
            return self._current_section.name
        return NEW_AREA_NAME if self._new_area_section else NEW_LINE_SECTION_NAME

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

    def _release_focus(self) -> None:
        """Release the focus of the button that started the editor.

        Key presses are ignored while a button has the focus. Releasing it enables
        the hotkeys of the editor right away.
        """
        if self._background_image is not None:
            self._background_image.client.run_javascript(RELEASE_FOCUS)

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
        self._sync_shift_anchor()
        self._update_shift_ring_timer()
        if self._overlay:
            self._overlay.content = (
                self._dim_svg()
                + self._sections.to_svg()
                + self._flows.to_svg(stale=self._flows_outdated)
                + self._edit_geometry()
                + self._new_section_svg()
                + self._action_pill_svg()
            )

    def _px(self, screen_pixels: float) -> float:
        """Length in image pixels of a length in screen pixels."""
        return screen_pixels * self._screen_scale

    def _is_action_pill_shown(self) -> bool:
        """The pill is always there while editing, except while a knob moves.

        A knob moves while it is dragged or picked up. Finishing then would save
        the knob wherever the mouse left it, e.g. under the pill.
        """
        return self._is_editor_active() and self._selected_knob_index is None

    def _action_anchor(self) -> Point | None:
        """Where the user acted last: the last knob placed or else the last knob.

        A placed knob that was deleted since is no anchor anymore.
        """
        if self._new_section and self._new_section_points:
            return self._new_section_points[-1].to_tuple()
        if self._current_section is not None:
            if self._last_placed_knob in self._edit_coordinates:
                return self._last_placed_knob
            if self._edit_temporary:
                return self._edit_temporary[-1]
        return None

    def _action_pill_center(self) -> Point:
        """Center of the pill, kept inside the image right below the anchor.

        The pill moves above the anchor if there is no room below. Without an
        anchor, the pill waits at the top of the image.
        """
        width, height = (
            self._current_image.size if self._current_image is not None else (0, 0)
        )
        half_width, half_height = self._px(WIDTH / 2), self._px(HEIGHT / 2)
        anchor = self._action_anchor()
        if anchor is None:
            return round(width / 2), round(2 * half_height)
        offset = self._px(ACTION_PILL_OFFSET)
        x: float = anchor[0]
        y = anchor[1] + offset
        if width:
            x = min(max(x, half_width), width - half_width)
        if height:
            if y + half_height > height:
                y = anchor[1] - offset
            y = min(max(y, half_height), height - half_height)
        return round(x), round(y)

    def _action_pill_svg(self) -> str:
        if not self._is_action_pill_shown():
            return ""
        center = self._action_pill_center()
        finish_enabled = not self._new_section or has_enough_knobs(
            circle_to_coordinates(self._new_section_points), self._new_area_section
        )
        return ActionPill(
            id=EDIT_ACTION_ID,
            x=center[0],
            y=center[1],
            finish_enabled=finish_enabled,
            finish_tooltip=self._resource_manager.get(
                CanvasKeys.TOOLTIP_FINISH_SECTION
            ),
            cancel_tooltip=self._resource_manager.get(
                CanvasKeys.TOOLTIP_CANCEL_SECTION
            ),
        ).to_svg()

    async def handle_svg_pointer_down(self, e: dict) -> None:
        """Run the action of the pill that was pressed, else select a knob."""
        if not self._accepts_input():
            return
        self._press_on_svg = True
        element_id = e.get(ELEMENT_ID) or ""
        if element_id.startswith(f"{EDIT_ACTION_ID}-") and (
            self._is_action_pill_shown()
        ):
            if element_id.endswith(f"-{FINISH_SUFFIX}"):
                await self._finish_editor()
            elif element_id.endswith(f"-{CANCEL_SUFFIX}"):
                self._cancel_action()
            self.draw_all()
            return
        self.on_svg_pointer_down(e)

    def _sync_shift_anchor(self) -> None:
        """Hide the shift ring if no knob is picked up or if it is dragged."""
        if self._selected_knob_index is None or self._dragging:
            self._shift_anchor = None
            self._shift_hovered_forward = None

    def _update_shift_ring_timer(self) -> None:
        """Poll for a still mouse only while a picked up knob waits for its ring."""
        if self._shift_ring_timer is None:
            return
        waiting = (
            self._selected_knob_index is not None
            and not self._dragging
            and self._shift_anchor is None
        )
        if self._shift_ring_timer.active != waiting:
            self._shift_ring_timer.active = waiting

    def _show_shift_ring_when_still(self) -> None:
        """Show the shift ring around the picked up knob once the mouse is still.

        The ring is placed around the knob. While the mouse stays inside the ring,
        the knob stays where it is so that the buttons of the ring can be reached.
        """
        index = self._selected_knob_index
        if index is None or self._dragging or self._shift_anchor is not None:
            return
        if time.monotonic() - self._last_knob_motion < SHIFT_RING_IDLE_SECONDS:
            return
        self._shift_anchor = self._edit_temporary[index]
        self.draw_all()

    def _shift_targets(self) -> dict[bool, int]:
        """Index of the knob swapped by a shift, for each available direction."""
        index = self._selected_knob_index
        if self._shift_anchor is None or index is None:
            return {}
        targets = {
            forward: shift_target_index(
                len(self._edit_temporary), index, forward, self._edit_is_area_section
            )
            for forward in (False, True)
        }
        return {
            forward: target for forward, target in targets.items() if target is not None
        }

    def _shift_ring_half_at(self, point: Point) -> bool | None:
        """Available half of the shift ring under the point."""
        if self._shift_anchor is None:
            return None
        half = ring_half_at(
            self._shift_anchor,
            point,
            self._px(SHIFT_RING_INNER_RADIUS),
            self._px(SHIFT_RING_OUTER_RADIUS),
        )
        return half if half in self._shift_targets() else None

    def _is_in_shift_ring(self, point: Point) -> bool:
        """Whether the point is on the ring or in its hole."""
        if self._shift_anchor is None:
            return False
        return (
            closest_knob_index(
                [self._shift_anchor], point, self._px(SHIFT_RING_OUTER_RADIUS)
            )
            is not None
        )

    def _shift_ring_svg(self) -> str:
        targets = self._shift_targets()
        if self._shift_anchor is None or not targets:
            return ""

        def label(forward: bool) -> str | None:
            if forward not in targets:
                return None
            return str(targets[forward] + 1)

        return ShiftRing(
            id=EDIT_SHIFT_ID,
            x=self._shift_anchor[0],
            y=self._shift_anchor[1],
            inner_radius=SHIFT_RING_INNER_RADIUS,
            outer_radius=SHIFT_RING_OUTER_RADIUS,
            backward_label=label(False),
            forward_label=label(True),
            backward_tooltip=self._resource_manager.get(
                CanvasKeys.TOOLTIP_SHIFT_KNOB_BACKWARD
            ),
            forward_tooltip=self._resource_manager.get(
                CanvasKeys.TOOLTIP_SHIFT_KNOB_FORWARD
            ),
            hovered_forward=self._shift_hovered_forward,
        ).to_svg()

    def _shift_partner_index(self) -> int | None:
        """Knob that swaps with the selected one if the hovered half is clicked."""
        if self._shift_hovered_forward is None:
            return None
        return self._shift_targets().get(self._shift_hovered_forward)

    def _shift_preview_svg(self) -> str:
        """Section geometry as it would be after shifting in the hovered direction.

        The current geometry is drawn as a ghost below it.
        """
        index = self._selected_knob_index
        if self._shift_hovered_forward is None or index is None:
            return ""
        shift = (
            shift_knob_forward if self._shift_hovered_forward else shift_knob_backward
        )
        coordinates, _ = shift(self._edit_temporary, index, self._edit_is_area_section)
        current = list(self._edit_temporary)
        if self._edit_is_area_section and current:
            current.append(current[0])
        return (
            Polyline(current).to_svg(GHOST_CLASS)
            + SectionShape(
                id=f"{EDIT_SHIFT_ID}-preview",
                points=coordinates,
                is_area=self._edit_is_area_section,
                editing=True,
                preview=True,
                show_points=False,
            ).to_svg()
        )

    @staticmethod
    def _shift_half_from_element_id(element_id: str | None) -> bool | None:
        if element_id == f"{EDIT_SHIFT_ID}-{FORWARD_SUFFIX}":
            return True
        if element_id == f"{EDIT_SHIFT_ID}-{BACKWARD_SUFFIX}":
            return False
        return None

    def _midpoints_svg(self) -> str:
        """Affordances to insert a knob. Drawn below the knobs, which win overlaps."""
        midpoints = segment_midpoints(self._edit_temporary, self._edit_is_area_section)
        return "".join(
            MidpointCircle(
                id=f"{EDIT_MIDPOINT_ID_PREFIX}{index}", x=point[0], y=point[1]
            ).to_svg()
            for index, point in enumerate(midpoints)
        )

    def _insert_knob_at_midpoint(self, segment: int) -> None:
        """Insert a knob at the segment midpoint and pick it up to be dragged.

        A segment that does not exist anymore, e.g. reported by the browser before
        it received the latest geometry, is ignored.
        """
        coordinates, index = insert_knob_at_segment(
            self._edit_temporary, segment, self._edit_is_area_section
        )
        if index is None:
            return
        self._edit_temporary, self._selected_knob_index = coordinates, index
        self._hovered_knob_index = None
        self._drop_on_release = False
        self._dragging = True
        self._knob_moved = False
        self.draw_all()

    def _dim_svg(self) -> str:
        if self._current_image is None:
            return ""
        width, height = self._current_image.size
        return f'<rect class="ota-dim" width="{width}" height="{height}"/>'

    def set_flows_outdated(self, outdated: bool) -> None:
        """Dim the flows while their track assignment is out of date."""
        self._flows_outdated = outdated
        self.draw_all()

    def _new_section_svg(self) -> str:
        coordinates = circle_to_coordinates(self._new_section_points)
        svg = ""
        if len(coordinates) >= 2:
            svg += SectionShape(
                id=NEW_SECTION_ID,
                points=coordinates,
                is_area=self._new_area_section,
                editing=True,
                show_points=False,
            ).to_svg()
        if self._new_section_points:
            points = "".join(
                dot(point.x, point.y, "pt-ring") + point.to_svg()
                for point in self._new_section_points
            )
            svg += f'<g class="ota-section editing">{points}</g>'
        if coordinates and self._preview_point:
            svg += Line(RUBBER_ID, *coordinates[-1], *self._preview_point).to_svg()
        return svg

    def _edit_geometry(self) -> str:
        if self._current_section is None:
            return ""
        svg = SectionShape(
            id=f"{self._current_section.id.id}-edit",
            points=self._edit_temporary,
            is_area=self._edit_is_area_section,
            editing=True,
            show_points=False,
        ).to_svg()
        if self._selected_knob_index is None:
            svg += self._midpoints_svg()
        svg += self._shift_preview_svg()
        partner = self._shift_partner_index()
        selected = self._selected_knob_index
        # The preview numbers the knobs in their new order.
        numbers = (
            {}
            if partner is None or selected is None
            else {
                selected: partner + 1,
                partner: selected + 1,
            }
        )
        for index, point in enumerate(self._edit_temporary):
            knob = create_knob(
                index,
                point,
                is_hovered=index == self._hovered_knob_index,
                is_selected=index == selected,
                is_partner=index == partner,
                number=numbers.get(index),
            )
            svg += knob.to_svg()
        return svg + self._shift_ring_svg()

    def on_mouse(self, e: events.MouseEventArguments) -> None:
        """Dispatch mouse events of the interactive image."""
        if not self._accepts_input():
            return
        point = to_point(e.image_x, e.image_y)
        if e.type == MOUSE_DOWN:
            self._press_on_svg = False
        elif e.type == MOUSE_MOVE:
            self._on_move(point)
        elif e.type == MOUSE_UP:
            self._on_release(point)
        elif e.type == CLICK:
            if self._press_on_svg:
                self._press_on_svg = False
                return
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
                self._last_knob_motion = time.monotonic()
                if self._is_in_shift_ring(point):
                    hovered = self._shift_ring_half_at(point)
                    changed = hovered != self._shift_hovered_forward
                    self._shift_hovered_forward = hovered
                    if changed:
                        self.draw_all()
                else:
                    self._shift_anchor = None
                    self._shift_hovered_forward = None
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
        self._last_placed_knob = point
        self._commit_edit()
        self._deselect_knob(revert=False)
        self._hovered_knob_index = index

    def _on_pointer_down(self, e: events.MouseEventArguments) -> None:
        if self._new_section:
            self._new_section_points.append(
                Circle(
                    id=f"new_point-{len(self._new_section_points)}",
                    x=round(e.image_x),
                    y=round(e.image_y),
                )
            )
            self.draw_all()

    def on_svg_pointer_down(self, e: dict) -> None:
        """Select a knob of the edited section or pick up the selected knob."""
        if self._current_section is None or not self._enabled:
            return
        point = svg_event_to_point(e)
        self._mouse_position = point
        self._last_knob_motion = time.monotonic()
        shift_forward = self._shift_half_from_element_id(e.get(ELEMENT_ID))
        if shift_forward in self._shift_targets():
            self._shift_selected_knob(forward=bool(shift_forward))
            return
        segment = midpoint_index_from_element_id(e.get(ELEMENT_ID))
        if segment is not None and self._selected_knob_index is None:
            self._insert_knob_at_midpoint(segment)
            return
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
            self._background_image.style(fit_into_workspace(*self._current_image.size))
            self._fit_overlay_to(self._current_image)
        else:
            self.clear_image()

    def _fit_overlay_to(self, image: Image.Image) -> None:
        """Size the overlay like the background, so the sections line up with it.

        The layer would take its size from the image's "loaded" event, which is
        lost if the image loads before the page is connected. Without a size the
        layer stays invisible.

        The layer has no source of its own. It scales the coordinates of its
        pointer events by its size, so without a size they are not in pixels of
        the image.
        """
        if self._overlay is None:
            return
        width, height = image.size
        self._overlay._props[SIZE_PROP] = (width, height)
        self._overlay.update()
        self._overlay.run_method(UPDATE_VIEWBOX, width, height)

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
        self._sections.add(
            SectionShape(
                id=id,
                points=open_area(coordinates, is_area_section),
                is_area=is_area_section,
                selected=is_selected_section,
                name=text,
            )
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
        self._update_editor_state()
        self._release_focus()
        self.draw_all()

    def draw_arrow(
        self,
        start_section: Section,
        end_section: Section,
        start_refpt_calculator: SectionRefPointCalculator,
        end_refpt_calculator: SectionRefPointCalculator,
        arrow_style: dict | None = None,
        tags: list[str] | None = None,
        count: int | None = None,
    ) -> None:
        start_x, start_y = start_refpt_calculator.get_reference_point(start_section)
        end_x, end_y = end_refpt_calculator.get_reference_point(end_section)
        arrow = Arrow(
            id=f"arrow-{start_section.id}-{end_section.id}",
            x1=int(start_x),
            x2=int(end_x),
            y1=int(start_y),
            y2=int(end_y),
            count=count,
        )
        self._flows.add(arrow)
        self.draw_all()

    def delete_element(self, tag_or_id: str) -> None:
        if tag_or_id == TAG_SELECTED_SECTION:
            return
        self._flows.clear()
        self._sections.clear()
        # Redraw, otherwise the overlay keeps showing what was removed until the
        # next item is drawn, e.g. after removing the last section.
        self.draw_all()

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
        self._update_editor_state()
        self._release_focus()
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
