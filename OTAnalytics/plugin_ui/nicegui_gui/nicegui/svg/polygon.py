from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import (
    Point,
    serialize_points,
)


@dataclass
class Polygon:
    """Closed shape, e.g. an area section."""

    points: list[Point]

    def to_svg(self, css_class: str) -> str:
        return (
            f'<polygon class="{css_class}" points="{serialize_points(self.points)}"/>'
        )
