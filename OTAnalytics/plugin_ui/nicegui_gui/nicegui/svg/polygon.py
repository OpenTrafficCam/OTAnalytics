from dataclasses import dataclass

AREA_FILL_OPACITY = 0.3


@dataclass
class Polygon:
    """Closed shape that is filled semi-transparently, e.g. an area section."""

    id: str
    points: list[tuple[int, int]]
    color: str
    fill_opacity: float = AREA_FILL_OPACITY

    def to_svg(self) -> str:
        return f"""<polygon id="{self.id}"
        points="{self.__serialized_points()}"
        stroke="{self.color}"
        fill="{self.color}"
        fill-opacity="{self.fill_opacity}" />"""

    def __serialized_points(self) -> str:
        return " ".join(f"{x},{y}" for x, y in self.points)
