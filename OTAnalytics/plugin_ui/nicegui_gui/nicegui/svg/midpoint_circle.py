from dataclasses import dataclass

MIDPOINT_CLASS = "ota-midpoint"
MIDPOINT_GLYPH_CLASS = "ota-midpoint-glyph"


@dataclass
class MidpointCircle:
    """Affordance in the middle of a segment, styled by the stylesheet.

    The colour is a fallback for a page without the stylesheet.
    """

    id: str
    x: int
    y: int
    color: str = "orange"
    radius: int = 14

    def to_svg(self) -> str:
        return (
            f'<circle id="{self.id}" class="{MIDPOINT_CLASS}" '
            f'cx="{self.x}" cy="{self.y}" r="{self.radius}" '
            f'fill="{self.color}" fill-opacity="0.7" '
            f'pointer-events="all" cursor="crosshair" />'
            f'<text class="{MIDPOINT_GLYPH_CLASS}" x="{self.x}" y="{self.y}" '
            f'text-anchor="middle" dominant-baseline="central" fill="white" '
            f'font-size="{self.radius + 3}" '
            f'pointer-events="none" style="user-select:none">+</text>'
        )
