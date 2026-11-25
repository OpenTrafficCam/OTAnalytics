from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.midpoint_circle import MidpointCircle


class TestMidpointCircle:
    def test_dot_carries_the_id_and_position(self) -> None:
        svg = MidpointCircle(id="edit-mid-3", x=100, y=200).to_svg()

        assert '<path id="edit-mid-3" class="ota-mid" d="M100 200h0"/>' in svg

    def test_plus_sign_is_sized_in_screen_pixels(self) -> None:
        svg = MidpointCircle(id="edit-mid-3", x=100, y=200).to_svg()

        assert '<g transform="translate(100 200)">' in svg
        assert 'class="ota-scaled ota-mid-plus"' in svg
        assert "M-5 0h10M0-5v10" in svg

    def test_markup_has_no_colors(self) -> None:
        svg = MidpointCircle(id="edit-mid-3", x=1, y=2).to_svg()

        for attribute in ["fill=", "stroke=", "font-size="]:
            assert attribute not in svg
