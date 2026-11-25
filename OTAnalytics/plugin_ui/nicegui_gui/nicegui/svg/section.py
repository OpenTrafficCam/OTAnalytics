from dataclasses import dataclass
from html import escape

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polygon import Polygon
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polyline import Polyline
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import Point, dot
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.text import Text

SHAPE_PARTS = ["glow", "casing", "line"]


@dataclass
class SectionShape:
    """Section drawn as a group, styled by its state classes.

    The points of an area are expected without the closing point.
    """

    id: str
    points: list[Point]
    is_area: bool = False
    selected: bool = False
    editing: bool = False
    name: str | None = None
    show_points: bool = True

    @property
    def shape(self) -> Polyline | Polygon:
        if self.is_area:
            return Polygon(self.points)
        return Polyline(self.points)

    def classes(self) -> str:
        states = [
            ("area", self.is_area),
            ("selected", self.selected),
            ("editing", self.editing),
        ]
        return " ".join(["ota-section"] + [name for name, on in states if on])

    def chip_anchor(self) -> tuple[float, float]:
        """First point of a line, centroid of the points of an area."""
        if not self.is_area:
            return self.points[0]
        count = len(self.points)
        return (
            sum(x for x, _ in self.points) / count,
            sum(y for _, y in self.points) / count,
        )

    def to_svg(self) -> str:
        shape = self.shape
        parts = [shape.to_svg(part) for part in SHAPE_PARTS]
        if self.show_points:
            for index, (x, y) in enumerate(self.points):
                parts.append(dot(x, y, "pt-ring"))
                parts.append(dot(x, y, "pt", f"{self.id}-{index}"))
        if self.name and self.points:
            parts.append(Text(*self.chip_anchor(), self.name).to_svg())
        return (
            f'<g id="{escape(self.id)}" class="{self.classes()}">'
            + "".join(parts)
            + "</g>"
        )
