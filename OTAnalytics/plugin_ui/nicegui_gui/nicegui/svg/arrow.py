import math
from dataclasses import dataclass
from html import escape

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import fmt, screen_px

CURVATURE = 0.12
BADGE_PADDING = 16
BADGE_CHARACTER_WIDTH = 7
HEAD = '<polygon class="head" points="0,0 -12,-5 -12,5"/>'


@dataclass
class Arrow:
    """Flow drawn as a curve from start to end, with its track count."""

    id: str
    x1: float
    y1: float
    x2: float
    y2: float
    count: int | None = None

    def control_point(self) -> tuple[float, float]:
        """Midpoint, moved left of the direction by 12 % of the length."""
        return (
            (self.x1 + self.x2) / 2 + CURVATURE * (self.y2 - self.y1),
            (self.y1 + self.y2) / 2 - CURVATURE * (self.x2 - self.x1),
        )

    def point_at(self, t: float) -> tuple[float, float]:
        cx, cy = self.control_point()
        a, b, c = (1 - t) ** 2, 2 * (1 - t) * t, t**2
        return (
            a * self.x1 + b * cx + c * self.x2,
            a * self.y1 + b * cy + c * self.y2,
        )

    def head_angle(self) -> float:
        cx, cy = self.control_point()
        return math.degrees(math.atan2(self.y2 - cy, self.x2 - cx))

    def to_svg(self, stale: bool = False) -> str:
        classes = "ota-flow stale" if stale else "ota-flow"
        cx, cy = self.control_point()
        d = (
            f"M{fmt(self.x1)} {fmt(self.y1)} "
            f"Q{fmt(cx)} {fmt(cy)} {fmt(self.x2)} {fmt(self.y2)}"
        )
        head = (
            f'<g transform="translate({fmt(self.x2)} {fmt(self.y2)}) '
            f'rotate({fmt(self.head_angle())})"><g class="ota-scaled">{HEAD}</g></g>'
        )
        return (
            f'<g id="{escape(self.id)}" class="{classes}">'
            f'<path class="casing" d="{d}"/><path class="line" d="{d}"/>'
            f"{head}{self._badge()}</g>"
        )

    def _badge(self) -> str:
        if self.count is None:
            return ""
        text = str(self.count)
        width = BADGE_PADDING + BADGE_CHARACTER_WIDTH * len(text)
        badge = (
            f'<rect x="{fmt(-width / 2)}" y="-10" width="{width}" height="20" '
            f'rx="10"/><text y="4">{text}</text>'
        )
        return screen_px(*self.point_at(0.5), badge, "ota-badge")
