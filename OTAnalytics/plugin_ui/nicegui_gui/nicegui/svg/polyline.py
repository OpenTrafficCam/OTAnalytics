from dataclasses import dataclass


@dataclass
class Polyline:
    id: str
    points: list[tuple[int, int]]
    color: str

    def to_svg(self) -> str:
        return f"""<polyline
        points="{self.__serialized_points()}"
        stroke="{self.color}"
        fill="none" />"""

    def __serialized_points(self) -> str:
        coordinates = [",".join([str(x) for x in e]) for e in self.points]
        return " ".join(coordinates)
