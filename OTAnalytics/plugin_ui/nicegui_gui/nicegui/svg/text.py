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
    css_class: str | None = None

    def to_svg(self) -> str:
        css_class = f' class="{escape(self.css_class)}"' if self.css_class else ""
        return f"""<text id="{escape(self.id)}"{css_class}
        x="{self.x}"
        y="{self.y}"
        fill="{self.color}"
        font-size="{self.font_size}"
        style="pointer-events: none">{escape(self.text)}</text>"""
