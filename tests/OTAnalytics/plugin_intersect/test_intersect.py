from shapely import GeometryCollection, LineString, Point, Polygon

from OTAnalytics.plugin_intersect.intersect import ShapelyIntersector


class TestShapelyIntersector:
    def test_line_intersects_line_true(self) -> None:
        first_line = LineString([[0, 0.5], [1, 0.5]])
        second_line = LineString([[0.5, 0], [0.5, 1]])

        intersector = ShapelyIntersector()
        intersects = intersector.line_intersects_line(first_line, second_line)

        assert intersects

    def test_line_intersects_line_false(self) -> None:
        first_line = LineString([[0, 0], [10, 0]])
        second_line = LineString([[0, 5], [10, 5]])

        intersector = ShapelyIntersector()
        intersects = intersector.line_intersects_line(first_line, second_line)

        assert not intersects

    def test_line_intersects_polygon_true(self) -> None:
        line = LineString([[5, 0], [5, 10]])
        polygon = Polygon(((0, 5), (5, 1), (10, 5), (5, 5), (0, 5)))

        intersector = ShapelyIntersector()
        intersects = intersector.line_intersects_polygon(line, polygon)

        assert intersects

    def test_line_intersects_polygon_false(self) -> None:
        line = LineString([[20, 0], [20, 10]])
        polygon = Polygon(((0, 5), (5, 1), (10, 5), (5, 5), (0, 5)))

        intersector = ShapelyIntersector()
        intersects = intersector.line_intersects_polygon(line, polygon)

        assert not intersects

    def test_intersection_line_with_line_exists(self) -> None:
        first_line = LineString([[0, 0.5], [1, 0.5]])
        second_line = LineString([[0.5, 0], [0.5, 1]])

        intersector = ShapelyIntersector()
        intersection = intersector.intersection_line_with_line(first_line, second_line)

        assert intersection == [Point(0.5, 0.5)]

    def test_intersection_line_with_line_does_not_exist(self) -> None:
        first_line = LineString([[0, 0], [10, 0]])
        second_line = LineString([[0, 5], [10, 5]])

        intersector = ShapelyIntersector()
        intersection = intersector.intersection_line_with_line(first_line, second_line)

        assert intersection is None

    def test_split_line_with_line_exists(self) -> None:
        first_line = LineString([[0, 0.5], [1, 0.5]])
        splitter = LineString([[0.5, 0], [0.5, 1]])

        intersector = ShapelyIntersector()
        splitted_lines = intersector.split_line_with_line(first_line, splitter)

        expected = GeometryCollection(
            [
                LineString([[0, 0.5], [0.5, 0.5]]),
                LineString([[0.5, 0.5], [1, 0.5]]),
            ]
        )
        assert splitted_lines == expected

    def test_split_line_with_line_does_not_exist(self) -> None:
        first_line = LineString([[0, 0], [10, 0]])
        splitter = LineString([[0, 5], [10, 5]])

        intersector = ShapelyIntersector()
        splitted_lines = intersector.split_line_with_line(first_line, splitter)

        expected = GeometryCollection([first_line])
        assert splitted_lines == expected

    def test_distance_point_point(self) -> None:
        first_point = Point(0, 0)
        second_point = Point(1, 0)

        intersector = ShapelyIntersector()
        distance = intersector.distance_point_point(first_point, second_point)

        assert distance == 1

    def test_are_points_within_polygon(self) -> None:
        coords = ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0))
        polygon = Polygon(coords)
        points: list[tuple[float, float]] = [
            (0.0, 0.0),
            (0.5, 0.5),
            (2.0, 2.0),
            (0.1, 0.0),
        ]

        intersector = ShapelyIntersector()
        result_mask = intersector.are_points_within_polygon(points, polygon)
        expected_mask = [False, True, False, False]

        assert result_mask == expected_mask
