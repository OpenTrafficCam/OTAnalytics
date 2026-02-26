from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.circle import Circle


class TestCircle:
    def test_circle_creation_with_required_params(self) -> None:
        # Arrange & Act
        circle = Circle(id="test-circle", x=100, y=200, fill="red", pointer_event="all")

        # Assert
        assert circle.id == "test-circle"
        assert circle.x == 100
        assert circle.y == 200
        assert circle.fill == "red"
        assert circle.pointer_event == "all"
        # Test default values
        assert circle.radius == 10
        assert circle.stroke == "blue"
        assert circle.stroke_width == 10
        assert circle.stroke_opacity == 0.0
        assert circle.cursor == "pointer"

    def test_circle_creation_with_all_params(self) -> None:
        # Arrange & Act
        circle = Circle(
            id="full-circle",
            x=50,
            y=75,
            fill="green",
            pointer_event="none",
            radius=20,
            stroke="red",
            stroke_width=5,
            stroke_opacity=0.5,
            cursor="crosshair",
        )

        # Assert
        assert circle.id == "full-circle"
        assert circle.x == 50
        assert circle.y == 75
        assert circle.fill == "green"
        assert circle.pointer_event == "none"
        assert circle.radius == 20
        assert circle.stroke == "red"
        assert circle.stroke_width == 5
        assert circle.stroke_opacity == 0.5
        assert circle.cursor == "crosshair"

    def test_circle_to_svg(self) -> None:
        # Arrange
        circle = Circle(id="svg-test", x=100, y=200, fill="blue", pointer_event="all")

        # Act
        svg = circle.to_svg()

        # Assert
        assert '<circle id="svg-test"' in svg
        assert 'cx="100"' in svg
        assert 'cy="200"' in svg
        assert 'r="10"' in svg  # default radius
        assert 'stroke="blue"' in svg  # default stroke
        assert 'stroke-width="10"' in svg  # default stroke_width
        assert 'stroke-opacity="0.0"' in svg  # default stroke_opacity
        assert 'fill="blue"' in svg
        assert "pointer-events=all" in svg
        assert 'cursor="pointer"' in svg  # default cursor

    def test_circle_to_svg_with_custom_values(self) -> None:
        # Arrange
        circle = Circle(
            id="custom-circle",
            x=300,
            y=400,
            fill="purple",
            pointer_event="none",
            radius=25,
            stroke="orange",
            stroke_width=3,
            stroke_opacity=0.8,
            cursor="grab",
        )

        # Act
        svg = circle.to_svg()

        # Assert
        assert '<circle id="custom-circle"' in svg
        assert 'cx="300"' in svg
        assert 'cy="400"' in svg
        assert 'r="25"' in svg
        assert 'stroke="orange"' in svg
        assert 'stroke-width="3"' in svg
        assert 'stroke-opacity="0.8"' in svg
        assert 'fill="purple"' in svg
        assert "pointer-events=none" in svg
        assert 'cursor="grab"' in svg

    def test_circle_to_tuple(self) -> None:
        # Arrange
        circle = Circle(
            id="tuple-test", x=150, y=250, fill="yellow", pointer_event="all"
        )

        # Act
        result = circle.to_tuple()

        # Assert
        assert result == (150, 250)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_circle_to_tuple_with_negative_coordinates(self) -> None:
        # Arrange
        circle = Circle(
            id="negative-coords", x=-50, y=-100, fill="black", pointer_event="all"
        )

        # Act
        result = circle.to_tuple()

        # Assert
        assert result == (-50, -100)

    def test_circle_to_tuple_with_zero_coordinates(self) -> None:
        # Arrange
        circle = Circle(id="zero-coords", x=0, y=0, fill="white", pointer_event="all")

        # Act
        result = circle.to_tuple()

        # Assert
        assert result == (0, 0)

    def test_circle_svg_with_special_characters_in_id(self) -> None:
        # Arrange
        circle = Circle(
            id="special-id-123_test", x=10, y=20, fill="gray", pointer_event="all"
        )

        # Act
        svg = circle.to_svg()

        # Assert
        assert 'id="special-id-123_test"' in svg

    def test_circle_svg_with_hex_color(self) -> None:
        # Arrange
        circle = Circle(
            id="hex-color",
            x=10,
            y=20,
            fill="#FF5733",
            pointer_event="all",
            stroke="#33FF57",
        )

        # Act
        svg = circle.to_svg()

        # Assert
        assert 'fill="#FF5733"' in svg
        assert 'stroke="#33FF57"' in svg
