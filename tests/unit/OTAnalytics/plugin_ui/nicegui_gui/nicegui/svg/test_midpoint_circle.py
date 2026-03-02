from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.midpoint_circle import MidpointCircle


class TestMidpointCircle:
    def test_default_values(self) -> None:
        mc = MidpointCircle(id="mid-sec1-0", x=100, y=200)
        assert mc.id == "mid-sec1-0"
        assert mc.x == 100
        assert mc.y == 200
        assert mc.color == "orange"
        assert mc.radius == 7

    def test_to_svg_contains_circle_element(self) -> None:
        mc = MidpointCircle(id="mid-sec1-0", x=100, y=200)
        svg = mc.to_svg()
        assert '<circle id="mid-sec1-0"' in svg
        assert 'cx="100"' in svg
        assert 'cy="200"' in svg
        assert 'r="7"' in svg
        assert 'pointer-events="all"' in svg
        assert 'cursor="crosshair"' in svg

    def test_to_svg_contains_plus_text(self) -> None:
        mc = MidpointCircle(id="mid-sec1-0", x=100, y=200)
        svg = mc.to_svg()
        assert ">+<" in svg
        assert 'pointer-events="none"' in svg

    def test_to_svg_custom_color(self) -> None:
        mc = MidpointCircle(id="mid-sec1-0", x=50, y=75, color="red", radius=10)
        svg = mc.to_svg()
        assert 'fill="red"' in svg
        assert 'r="10"' in svg
