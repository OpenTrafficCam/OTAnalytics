from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import dot, screen_px

MIDPOINT_CLASS = "ota-mid"
MIDPOINT_PLUS_CLASS = "ota-mid-plus"
PLUS_PATH = '<path d="M-5 0h10M0-5v10"/>'


@dataclass
class MidpointCircle:
    """Affordance in the middle of a segment to insert a knob.

    The dot receives the pointer events and carries the id. Its plus sign is
    sized in screen pixels. Colours and sizes are set by otanalytics.css.
    """

    id: str
    x: int
    y: int

    def to_svg(self) -> str:
        return dot(self.x, self.y, MIDPOINT_CLASS, self.id) + screen_px(
            self.x, self.y, PLUS_PATH, MIDPOINT_PLUS_CLASS
        )
