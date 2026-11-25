from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import fmt


@dataclass
class Line:
    """Rubber band from the last point of a new section to the mouse."""

    id: str
    x1: int
    y1: int
    x2: int
    y2: int

    def to_svg(self) -> str:
        return (
            f'<line class="ota-rubber" x1="{fmt(self.x1)}" y1="{fmt(self.y1)}" '
            f'x2="{fmt(self.x2)}" y2="{fmt(self.y2)}"/>'
        )
