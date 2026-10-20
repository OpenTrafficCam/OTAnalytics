from dataclasses import dataclass
from html import escape

BACKWARD_SUFFIX = "backward"
FORWARD_SUFFIX = "forward"
FONT_SIZE = 11


@dataclass
class ShiftRing:
    """Ring around a knob, split in a backward (left) and forward (right) half.

    Each half is a button that shows the position the knob would get. A half
    without label is not available and not drawn. `hovered_forward` highlights the
    half under the mouse (True: forward half, False: backward half).
    """

    id: str
    x: int
    y: int
    inner_radius: int
    outer_radius: int
    backward_label: str | None
    forward_label: str | None
    hovered_forward: bool | None = None
    fill: str = "royalblue"
    hovered_fill: str = "dodgerblue"
    color: str = "white"

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
                self.hovered_forward is False,
            )
        if self.forward_label is not None:
            svg += self._half(
                self.forward_id, True, self.forward_label, self.hovered_forward is True
            )
        return svg

    def _half(self, id: str, forward: bool, label: str, hovered: bool) -> str:
        x, y = self.x, self.y
        inner, outer = self.inner_radius, self.outer_radius
        # The forward half spans the right side of the ring, the backward half the
        # left side. Both are drawn clockwise along the outer arc.
        top, bottom = y - outer, y + outer
        inner_top, inner_bottom = y - inner, y + inner
        if forward:
            path = (
                f"M {x} {top} A {outer} {outer} 0 0 1 {x} {bottom} "
                f"L {x} {inner_bottom} A {inner} {inner} 0 0 0 {x} {inner_top} Z"
            )
            text_x = x + (inner + outer) // 2
        else:
            path = (
                f"M {x} {bottom} A {outer} {outer} 0 0 1 {x} {top} "
                f"L {x} {inner_top} A {inner} {inner} 0 0 0 {x} {inner_bottom} Z"
            )
            text_x = x - (inner + outer) // 2
        fill = self.hovered_fill if hovered else self.fill
        return (
            f'<path id="{escape(id)}" d="{path}" fill="{fill}" fill-opacity="0.9" '
            f'stroke="{self.color}" stroke-width="1" '
            f'pointer-events="all" cursor="pointer" />'
            f'<text x="{text_x}" y="{y}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{self.color}" '
            f'font-size="{FONT_SIZE}" pointer-events="none" '
            f'style="user-select:none">{escape(label)}</text>'
        )
