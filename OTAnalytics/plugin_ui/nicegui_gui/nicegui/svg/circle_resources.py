from collections import defaultdict
from dataclasses import dataclass, field

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.circle import Circle


def default_factory() -> dict[str, dict[str, Circle]]:
    return defaultdict(dict)


@dataclass
class CircleResources:
    circles: dict[str, Circle]
    by_section: dict[str, dict[str, Circle]] = field(default_factory=default_factory)

    def to_svg(self) -> str:
        return "\n".join([circle.to_svg() for circle in self.circles.values()])

    def add(self, section_id: str, circle: Circle) -> None:
        self.circles[circle.id] = circle
        self.by_section[section_id][circle.id] = circle

    def clear(self) -> None:
        self.circles.clear()
