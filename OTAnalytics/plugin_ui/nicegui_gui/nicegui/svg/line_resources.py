from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.arrow import Arrow
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line import Line


@dataclass
class LineResources:
    lines: dict[str, Line | Arrow]

    def to_svg(self) -> str:
        return "\n".join([line.to_svg() for line in self.lines.values()])

    def add(self, line: Line | Arrow) -> None:
        self.lines[line.id] = line

    def clear(self) -> None:
        self.lines.clear()
