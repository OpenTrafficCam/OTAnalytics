from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polyline import Polyline


class TestPolyline:
    def test_polyline_creation(self) -> None:
        # Arrange & Act
        points = [(10, 20), (30, 40), (50, 60)]
        polyline = Polyline(id="test-polyline", points=points, color="blue")

        # Assert
        assert polyline.id == "test-polyline"
        assert polyline.points == points
        assert polyline.color == "blue"

    def test_polyline_to_svg(self) -> None:
        # Arrange
        points = [(10, 20), (30, 40), (50, 60)]
        polyline = Polyline(id="test-polyline", points=points, color="blue")

        # Act
        svg = polyline.to_svg()

        # Assert
        assert "<polyline" in svg
        assert 'points="10,20 30,40 50,60"' in svg
        assert 'stroke="blue"' in svg
        assert 'fill="none"' in svg

    def test_polyline_to_svg_with_single_point(self) -> None:
        # Arrange
        points = [(100, 200)]
        polyline = Polyline(id="single-point", points=points, color="red")

        # Act
        svg = polyline.to_svg()

        # Assert
        assert 'points="100,200"' in svg
        assert 'stroke="red"' in svg

    def test_polyline_to_svg_with_empty_points(self) -> None:
        # Arrange
        points: list[tuple[int, int]] = []
        polyline = Polyline(id="empty-polyline", points=points, color="green")

        # Act
        svg = polyline.to_svg()

        # Assert
        assert 'points=""' in svg
        assert 'stroke="green"' in svg

    def test_polyline_serialized_points_formatting(self) -> None:
        # Arrange
        points = [(0, 0), (100, 100), (200, 50)]
        polyline = Polyline(id="format-test", points=points, color="black")

        # Act
        svg = polyline.to_svg()

        # Assert
        assert 'points="0,0 100,100 200,50"' in svg

    def test_polyline_with_large_coordinates(self) -> None:
        # Arrange
        points = [(1000, 2000), (3000, 4000)]
        polyline = Polyline(id="large-coords", points=points, color="purple")

        # Act
        svg = polyline.to_svg()

        # Assert
        assert 'points="1000,2000 3000,4000"' in svg
        assert 'stroke="purple"' in svg

    def test_polyline_with_negative_coordinates(self) -> None:
        # Arrange
        points = [(-10, -20), (30, -40), (-50, 60)]
        polyline = Polyline(id="negative-coords", points=points, color="orange")

        # Act
        svg = polyline.to_svg()

        # Assert
        assert 'points="-10,-20 30,-40 -50,60"' in svg
        assert 'stroke="orange"' in svg
