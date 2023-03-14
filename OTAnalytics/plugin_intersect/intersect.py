from shapely import LineString, Polygon


class ShapelyIntersector:
    def line_intersects_line(self, line_1: LineString, line_2: LineString) -> bool:
        return line_1.intersects(line_2)

    def line_intersects_polygon(self, line: LineString, polygon: Polygon) -> bool:
        return line.intersects(polygon)
