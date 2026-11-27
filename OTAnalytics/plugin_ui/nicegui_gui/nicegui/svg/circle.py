from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import dot


@dataclass
class Circle:
    """Point of a section, e.g. while a new section is drawn."""

    id: str
    x: int
    y: int

    def to_svg(self) -> str:
        return dot(self.x, self.y, "pt", self.id)

    def to_tuple(self) -> tuple[int, int]:
        return self.x, self.y
