from dataclasses import dataclass


@dataclass
class Line:
    id: str
    x1: int
    y1: int
    x2: int
    y2: int
    stroke: str

    def to_svg(self) -> str:
        return f"""<line x1="{self.x1}" y1="{self.y1}"
        x2="{self.x2}" y2="{self.y2}" stroke={self.stroke} />"""
