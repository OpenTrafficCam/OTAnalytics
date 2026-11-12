from dataclasses import dataclass, field

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polygon import Polygon
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polyline import Polyline
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.text import Text


@dataclass
class SectionResource:
    lines: dict[str, Polyline | Polygon]
    texts: dict[str, Text] = field(default_factory=dict)

    def to_svg(self) -> str:
        shapes = [line.to_svg() for line in self.lines.values()]
        texts = [text.to_svg() for text in self.texts.values()]
        return "\n".join(shapes + texts)

    def clear(self) -> None:
        self.lines.clear()
        self.texts.clear()

    def add(self, section_id: str, line: Polyline | Polygon) -> None:
        self.lines[section_id] = line

    def add_text(self, section_id: str, text: Text) -> None:
        self.texts[section_id] = text
