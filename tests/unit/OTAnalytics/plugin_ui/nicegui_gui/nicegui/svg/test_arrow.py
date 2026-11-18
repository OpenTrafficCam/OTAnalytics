from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.arrow import Arrow


class TestArrow:
    def test_arrow_to_svg(self) -> None:
        arrow = Arrow(
            id="arrow", x1=0, y1=0, x2=100, y2=0, color="red", width=4, dash=(5, 5)
        )

        svg = arrow.to_svg()

        assert 'id="arrow"' in svg
        assert '<line x1="0" y1="0" x2="100" y2="0"' in svg
        assert 'stroke="red"' in svg
        assert 'stroke-width="4"' in svg
        assert 'stroke-dasharray="5 5"' in svg
        assert "<polygon" in svg
        assert 'fill="red"' in svg

    def test_arrow_head_points_to_end(self) -> None:
        arrow = Arrow(
            id="arrow",
            x1=0,
            y1=0,
            x2=100,
            y2=0,
            color="red",
            head_length=20,
            head_half_width=8,
        )

        assert arrow.head_points() == [(100.0, 0.0), (80.0, 8.0), (80.0, -8.0)]

    def test_arrow_without_dash(self) -> None:
        arrow = Arrow(id="arrow", x1=0, y1=0, x2=100, y2=0, color="red")

        assert "stroke-dasharray" not in arrow.to_svg()

    def test_arrow_without_length_has_no_head(self) -> None:
        arrow = Arrow(id="arrow", x1=10, y1=10, x2=10, y2=10, color="red")

        assert arrow.head_points() == []
        assert "<polygon" not in arrow.to_svg()
