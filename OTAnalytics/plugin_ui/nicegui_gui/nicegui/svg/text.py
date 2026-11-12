from dataclasses import dataclass
from html import escape

DEFAULT_FONT_SIZE = 14


@dataclass
class Text:
    id: str
    x: int
    y: int
    text: str
    color: str
    font_size: int = DEFAULT_FONT_SIZE

    def to_svg(self) -> str:
        return f"""<text id="{escape(self.id)}"
        x="{self.x}"
        y="{self.y}"
        fill="{self.color}"
        font-size="{self.font_size}"
        pointer-events="none">{escape(self.text)}</text>"""
