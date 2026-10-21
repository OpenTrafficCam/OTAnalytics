import math
from dataclasses import dataclass

DEFAULT_ARROW_WIDTH = 2
DEFAULT_HEAD_LENGTH = 20
DEFAULT_HEAD_HALF_WIDTH = 8


@dataclass
class Arrow:
    """Line from start to end with an arrow head at the end, e.g. a flow."""

    id: str
    x1: int
    y1: int
    x2: int
    y2: int
    color: str
    width: int = DEFAULT_ARROW_WIDTH
    dash: tuple[int, ...] | None = None
    head_length: int = DEFAULT_HEAD_LENGTH
    head_half_width: int = DEFAULT_HEAD_HALF_WIDTH

    def to_svg(self) -> str:
        dash = (
            f' stroke-dasharray="{" ".join(str(d) for d in self.dash)}"'
            if self.dash
            else ""
        )
        svg = f"""<g id="{self.id}">
        <line x1="{self.x1}" y1="{self.y1}" x2="{self.x2}" y2="{self.y2}"
        stroke="{self.color}" stroke-width="{self.width}"{dash} />"""
        if head := self.head_points():
            points = " ".join(f"{x},{y}" for x, y in head)
            svg += f"""
        <polygon points="{points}" fill="{self.color}" />"""
        return svg + "</g>"

    def head_points(self) -> list[tuple[float, float]]:
        """Corners of the arrow head: tip and the two trailing points."""
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        length = math.hypot(dx, dy)
        if length == 0:
            return []
        ux, uy = dx / length, dy / length
        base_x = self.x2 - ux * self.head_length
        base_y = self.y2 - uy * self.head_length
        nx, ny = -uy * self.head_half_width, ux * self.head_half_width
        return [
            (float(self.x2), float(self.y2)),
            (base_x + nx, base_y + ny),
            (base_x - nx, base_y - ny),
        ]
