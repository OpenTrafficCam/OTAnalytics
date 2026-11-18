from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.polygon import Polygon


class TestPolygon:
    def test_polygon_to_svg(self) -> None:
        polygon = Polygon(
            id="area", points=[(0, 0), (10, 0), (10, 10)], color="red", fill_opacity=0.3
        )

        svg = polygon.to_svg()

        assert "<polygon" in svg
        assert 'id="area"' in svg
        assert 'points="0,0 10,0 10,10"' in svg
        assert 'stroke="red"' in svg
        assert 'fill="red"' in svg
        assert 'fill-opacity="0.3"' in svg

    def test_polygon_is_semi_transparent_by_default(self) -> None:
        polygon = Polygon(id="area", points=[(0, 0), (10, 0), (10, 10)], color="red")

        assert 0 < polygon.fill_opacity < 1
