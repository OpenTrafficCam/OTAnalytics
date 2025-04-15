from dataclasses import dataclass

from OTAnalytics.domain.section import SectionId
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line import Line


@dataclass
class SectionResource:
    lines: dict[SectionId, Line]

    def to_svg(self) -> str:
        return "\n".join(line.to_svg() for line in self.lines.values())

    def clear(self) -> None:
        self.lines.clear()
