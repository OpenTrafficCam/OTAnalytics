from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import (
    Point,
    serialize_points,
)


@dataclass
class Polyline:
    points: list[Point]

    def to_svg(self, css_class: str) -> str:
        return (
            f'<polyline class="{css_class}" points="{serialize_points(self.points)}"/>'
        )
