from dataclasses import dataclass
from html import escape

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import fmt, screen_px

BACKWARD_SUFFIX = "backward"
FORWARD_SUFFIX = "forward"

RING_CLASS = "ota-shift"
HALF_CLASS = "half"
HOVERED_CLASS = "hovered"
LABEL_CLASS = "label"
CHEVRON_CLASS = "chev"
UNAVAILABLE_CLASS = "unavailable"

# Positions in screen pixels, measured from the center along the x axis
CHEVRON_X = 33
NUMBER_X = 25
# Half of the gap between the halves
HALF_GAP = 1.5
BACKWARD_CHEVRON = "M-4-4l-4 4 4 4"
FORWARD_CHEVRON = "M4-4l4 4-4 4"


@dataclass
class ShiftRing:
    """Ring around a knob, split in a backward (left) and forward (right) half.

    Each half is a button that shows a chevron and the position the knob would
    get. A half without label is not available. It is drawn as an outline without
    id, so the ring keeps its shape. `hovered_forward` marks the half under the
    mouse (True: forward half, False: backward half).

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
        svg = self._half(
            self.backward_id,
            False,
            self.backward_label,
            self.backward_tooltip,
            self.hovered_forward is False,
        ) + self._half(
            self.forward_id,
            True,
            self.forward_label,
            self.forward_tooltip,
            self.hovered_forward is True,
        )
        return screen_px(self.x, self.y, svg, RING_CLASS)

    def _half(
        self,
        id: str,
        forward: bool,
        label: str | None,
        tooltip: str,
        hovered: bool,
    ) -> str:
        """One half in a group of its own.

        Hovering a half restyles its siblings, so the group keeps that from
        reaching the other half. The group is moved outwards to split the gap
        between the halves.
        """
        path = self._path(forward)
        sign = 1 if forward else -1
        group = f'<g transform="translate({fmt(sign * HALF_GAP)} 0)">'
        if label is None:
            return (
                f'{group}<path class="{HALF_CLASS} {UNAVAILABLE_CLASS}" '
                f'd="{path}"/></g>'
            )
        css_class = f"{HALF_CLASS} {HOVERED_CLASS}" if hovered else HALF_CLASS
        chevron = FORWARD_CHEVRON if forward else BACKWARD_CHEVRON
        return (
            f"{group}"
            f'<path id="{escape(id)}" class="{css_class}" d="{path}">'
            f"<title>{escape(tooltip)}</title></path>"
            f'<path class="{CHEVRON_CLASS}" d="{chevron}" '
            f'transform="translate({sign * CHEVRON_X} 0)"/>'
            f'<text class="{LABEL_CLASS}" x="{sign * NUMBER_X}" y="0">'
            f"{escape(label)}</text></g>"
        )

    def _path(self, forward: bool) -> str:
        """The forward half spans the right side of the ring, the backward half
        the left side. Both are drawn along the outer arc."""
        inner, outer = self.inner_radius, self.outer_radius
        if forward:
            return (
                f"M0-{outer}A{outer} {outer} 0 0 1 0 {outer}"
                f"L0 {inner}A{inner} {inner} 0 0 0 0-{inner}Z"
            )
        return (
            f"M0 {outer}A{outer} {outer} 0 0 1 0-{outer}"
            f"L0-{inner}A{inner} {inner} 0 0 0 0 {inner}Z"
        )
