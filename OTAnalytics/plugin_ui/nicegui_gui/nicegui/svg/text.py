from dataclasses import dataclass
from html import escape

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import screen_px

CHIP_OFFSET_X = 8
CHIP_OFFSET_Y = -30
CHIP_PADDING = 16
CHIP_CHARACTER_WIDTH = 7


@dataclass
class Text:
    """Chip with the name of a section, placed above and right of a point."""

    x: float
    y: float
    text: str

    def to_svg(self) -> str:
        width = CHIP_PADDING + CHIP_CHARACTER_WIDTH * len(self.text)
        # The offset is in screen pixels, so it is scaled with the chip.
        chip = (
            f'<g transform="translate({CHIP_OFFSET_X} {CHIP_OFFSET_Y})">'
            f'<rect width="{width}" height="22" rx="6"/>'
            f'<text x="8" y="15">{escape(self.text)}</text></g>'
        )
        return screen_px(self.x, self.y, chip, "ota-chip")
