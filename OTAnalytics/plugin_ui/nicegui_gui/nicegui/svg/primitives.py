"""Building blocks of the canvas overlay markup.

The markup carries geometry and state classes only. Its styling lives in
otanalytics.css (see docs/otanalytics-overlay-spec.md).
"""

from html import escape

Point = tuple[int, int]


def fmt(value: float) -> str:
    """Format a coordinate with at most one decimal and no trailing zero."""
    text = f"{round(value, 1):.1f}".rstrip("0").rstrip(".")
    return "0" if text == "-0" else text


def serialize_points(points: list[Point]) -> str:
    return " ".join(f"{x},{y}" for x, y in points)


def dot(x: float, y: float, css_class: str, id: str | None = None) -> str:
    """Zero-length path, drawn as a dot whose size is its stroke width."""
    id_attribute = f'id="{escape(id)}" ' if id is not None else ""
    return f'<path {id_attribute}class="{css_class}" d="M{fmt(x)} {fmt(y)}h0"/>'


def screen_px(x: float, y: float, inner: str, css_class: str = "") -> str:
    """Place content sized in screen pixels at an image position."""
    classes = f"ota-scaled {css_class}".strip()
    return (
        f'<g transform="translate({fmt(x)} {fmt(y)})">'
        f'<g class="{classes}">{inner}</g></g>'
    )
