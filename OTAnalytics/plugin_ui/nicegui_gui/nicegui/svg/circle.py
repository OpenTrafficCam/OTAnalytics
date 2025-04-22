from dataclasses import dataclass


@dataclass
class Circle:
    id: str
    x: int
    y: int
    fill: str
    pointer_event: str
    radius: int = 10
    stroke: str = "blue"
    stroke_width: int = 10
    stroke_opacity: float = 0.0
    cursor: str = "pointer"

    def to_svg(self) -> str:
        return f"""<circle id="{self.id}"
        cx="{self.x}"
        cy="{self.y}"
        r="{self.radius}"
        stroke="{self.stroke}"
        stroke-width="{self.stroke_width}"
        stroke-opacity="{self.stroke_opacity}"
        fill="{self.fill}"
        pointer-events={self.pointer_event}
        cursor="{self.cursor}" />"""

    def to_tuple(self) -> tuple[int, int]:
        return self.x, self.y
