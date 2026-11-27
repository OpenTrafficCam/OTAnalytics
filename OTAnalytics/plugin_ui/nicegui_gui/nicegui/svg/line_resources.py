from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.arrow import Arrow


@dataclass
class LineResources:
    lines: dict[str, Arrow]

    def to_svg(self, stale: bool = False) -> str:
        return "".join(line.to_svg(stale) for line in self.lines.values())

    def add(self, line: Arrow) -> None:
        self.lines[line.id] = line

    def clear(self) -> None:
        self.lines.clear()
