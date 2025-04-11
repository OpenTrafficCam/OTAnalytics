from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line import Line


@dataclass
class LineResources:
    lines: dict[str, Line]

    def to_svg(self) -> str:
        return "\n".join(self.lines)

    def add(self, line: Line) -> None:
        self.lines[line.id] = line
