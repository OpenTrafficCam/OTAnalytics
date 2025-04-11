from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.circle import Circle


@dataclass
class CircleResources:
    circles: dict[str, Circle]

    def to_svg(self) -> str:
        return "\n".join(self.circles)

    def add(self, circle: Circle) -> None:
        self.circles[circle.id] = circle
