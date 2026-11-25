from dataclasses import dataclass
from html import escape

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import screen_px

BACKWARD_SUFFIX = "backward"
FORWARD_SUFFIX = "forward"

RING_CLASS = "ota-shift"
HALF_CLASS = "half"
HOVERED_CLASS = "hovered"
LABEL_CLASS = "label"


@dataclass
class ShiftRing:
    """Ring around a knob, split in a backward (left) and forward (right) half.

    Each half is a button that shows the position the knob would get. A half
    without label is not available and not drawn. `hovered_forward` marks the
    half under the mouse (True: forward half, False: backward half).

    The radii are screen pixels. The ring is centered on x, y of the image.
    Colours and fonts are set by otanalytics.css.
    """

    id: str
    x: int
    y: int
    inner_radius: int
    outer_radius: int
    backward_label: str | None
    forward_label: str | None
    backward_tooltip: str = ""
    forward_tooltip: str = ""
    hovered_forward: bool | None = None

    @property
    def backward_id(self) -> str:
        return f"{self.id}-{BACKWARD_SUFFIX}"

    @property
    def forward_id(self) -> str:
        return f"{self.id}-{FORWARD_SUFFIX}"

    def to_svg(self) -> str:
        svg = ""
        if self.backward_label is not None:
            svg += self._half(
                self.backward_id,
                False,
                self.backward_label,
                self.backward_tooltip,
                self.hovered_forward is False,
            )
        if self.forward_label is not None:
            svg += self._half(
                self.forward_id,
                True,
                self.forward_label,
                self.forward_tooltip,
                self.hovered_forward is True,
            )
        return screen_px(self.x, self.y, svg, RING_CLASS)

    def _half(
        self, id: str, forward: bool, label: str, tooltip: str, hovered: bool
    ) -> str:
        inner, outer = self.inner_radius, self.outer_radius
        # The forward half spans the right side of the ring, the backward half the
        # left side. Both are drawn along the outer arc.
        if forward:
            path = (
                f"M0-{outer}A{outer} {outer} 0 0 1 0 {outer}"
                f"L0 {inner}A{inner} {inner} 0 0 0 0-{inner}Z"
            )
            text_x = (inner + outer) // 2
        else:
            path = (
                f"M0 {outer}A{outer} {outer} 0 0 1 0-{outer}"
                f"L0-{inner}A{inner} {inner} 0 0 0 0 {inner}Z"
            )
            text_x = -(inner + outer) // 2
        css_class = f"{HALF_CLASS} {HOVERED_CLASS}" if hovered else HALF_CLASS
        return (
            f'<path id="{escape(id)}" class="{css_class}" d="{path}">'
            f"<title>{escape(tooltip)}</title></path>"
            f'<text class="{LABEL_CLASS}" x="{text_x}" y="0">{escape(label)}</text>'
        )
