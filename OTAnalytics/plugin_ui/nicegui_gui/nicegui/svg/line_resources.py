from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line import Line


@dataclass
class LineResources:
    lines: dict[str, Line]

    def to_svg(self) -> str:
        return "\n".join([line.to_svg() for line in self.lines.values()])

    def add(self, line: Line) -> None:
        self.lines[line.id] = line

    def clear(self) -> None:
        self.lines.clear()
