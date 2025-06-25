from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polyline import Polyline


@dataclass
class SectionResource:
    lines: dict[str, Polyline]

    def to_svg(self) -> str:
        return "\n".join(line.to_svg() for line in self.lines.values())

    def clear(self) -> None:
        self.lines.clear()

    def add(self, section_id: str, line: Polyline) -> None:
        self.lines[section_id] = line
