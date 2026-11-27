from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import dot, fmt

MIDPOINT_CLASS = "ota-mid"
MIDPOINT_CORE_CLASS = "ota-mid-core"
MIDPOINT_PLUS_CLASS = "ota-mid-plus"
PLUS_PATH = '<path d="M-5 0h10M0-5v10"/>'


@dataclass
class MidpointCircle:
    """Affordance in the middle of a segment to insert a knob.

    The edge dot receives the pointer events and carries the id. The core dot and
    the plus sign follow it as siblings, so hovering the edge restyles them. Each
    midpoint is a group of its own, which keeps that from reaching other
    midpoints. The plus sign is sized in screen pixels. Colours and sizes are set
    by otanalytics.css.
    """

    id: str
    x: int
    y: int

    def to_svg(self) -> str:
        plus = (
            f'<g class="{MIDPOINT_PLUS_CLASS}" '
            f'transform="translate({fmt(self.x)} {fmt(self.y)})">'
            f'<g class="ota-scaled">{PLUS_PATH}</g></g>'
        )
        return (
            "<g>"
            + dot(self.x, self.y, MIDPOINT_CLASS, self.id)
            + dot(self.x, self.y, MIDPOINT_CORE_CLASS)
            + plus
            + "</g>"
        )
