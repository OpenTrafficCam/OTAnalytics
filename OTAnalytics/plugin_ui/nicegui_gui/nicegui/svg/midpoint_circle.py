from dataclasses import dataclass


@dataclass
class MidpointCircle:
    id: str
    x: int
    y: int
    color: str = "orange"
    radius: int = 7

    def to_svg(self) -> str:
        return (
            f'<circle id="{self.id}" cx="{self.x}" cy="{self.y}" r="{self.radius}" '
            f'fill="{self.color}" fill-opacity="0.7" '
            f'pointer-events="all" cursor="crosshair" />'
            f'<text x="{self.x}" y="{self.y}" text-anchor="middle" '
            f'dominant-baseline="central" fill="white" font-size="{self.radius + 3}" '
            f'pointer-events="none" style="user-select:none">+</text>'
        )
