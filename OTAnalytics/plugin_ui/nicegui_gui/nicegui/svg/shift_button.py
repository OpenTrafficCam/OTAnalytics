from dataclasses import dataclass
from html import escape


@dataclass
class ShiftButton:
    """Round button with a glyph, e.g. an arrow, that receives pointer events."""

    id: str
    x: int
    y: int
    glyph: str
    radius: int = 12
    color: str = "white"
    fill: str = "royalblue"

    def to_svg(self) -> str:
        return (
            f'<circle id="{escape(self.id)}" cx="{self.x}" cy="{self.y}" '
            f'r="{self.radius}" fill="{self.fill}" fill-opacity="0.9" '
            f'stroke="{self.color}" stroke-width="1" '
            f'pointer-events="all" cursor="pointer" />'
            f'<text x="{self.x}" y="{self.y}" text-anchor="middle" '
            f'dominant-baseline="central" fill="{self.color}" '
            f'font-size="{self.radius}" pointer-events="none" '
            f'style="user-select:none">{escape(self.glyph)}</text>'
        )
