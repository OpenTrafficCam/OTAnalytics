from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line import Line


class TestLine:
    def test_line_creation(self) -> None:
        # Arrange & Act
        line = Line(id="test-line", x1=10, y1=20, x2=30, y2=40, stroke="red")

        # Assert
        assert line.id == "test-line"
        assert line.x1 == 10
        assert line.y1 == 20
        assert line.x2 == 30
        assert line.y2 == 40
        assert line.stroke == "red"

    def test_line_to_svg(self) -> None:
        # Arrange
        line = Line(id="test-line", x1=10, y1=20, x2=30, y2=40, stroke="red")

        # Act
        svg = line.to_svg()

        # Assert
        assert '<line x1="10" y1="20"' in svg
        assert 'x2="30" y2="40" stroke=red' in svg
        assert "test-line" not in svg  # ID is not included in SVG output

    def test_line_to_svg_with_different_coordinates(self) -> None:
        # Arrange
        line = Line(id="another-line", x1=100, y1=200, x2=300, y2=400, stroke="blue")

        # Act
        svg = line.to_svg()

        # Assert
        assert '<line x1="100" y1="200"' in svg
        assert 'x2="300" y2="400" stroke=blue' in svg

    def test_line_to_svg_with_special_stroke_color(self) -> None:
        # Arrange
        line = Line(id="special-line", x1=0, y1=0, x2=50, y2=50, stroke="#FF5733")

        # Act
        svg = line.to_svg()

        # Assert
        assert "stroke=#FF5733" in svg
