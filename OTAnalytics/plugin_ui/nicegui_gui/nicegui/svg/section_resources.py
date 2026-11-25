from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.section import SectionShape


@dataclass
class SectionResource:
    sections: dict[str, SectionShape]

    def to_svg(self) -> str:
        return "".join(section.to_svg() for section in self.sections.values())

    def clear(self) -> None:
        self.sections.clear()

    def add(self, section: SectionShape) -> None:
        self.sections[section.id] = section
