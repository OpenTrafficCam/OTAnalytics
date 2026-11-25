from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.shift_ring import ShiftRing


def ring(**kwargs: object) -> ShiftRing:
    values: dict = dict(
        id="ring",
        x=100,
        y=50,
        inner_radius=16,
        outer_radius=46,
        backward_label="◀1",
        forward_label="3▶",
    )
    values.update(kwargs)
    return ShiftRing(**values)


class TestShiftRing:
    def test_has_ids_for_each_half(self) -> None:
        assert ring().backward_id == "ring-backward"
        assert ring().forward_id == "ring-forward"

    def test_is_centered_on_the_knob_in_screen_pixels(self) -> None:
        svg = ring().to_svg()

        assert svg.startswith('<g transform="translate(100 50)">')
        assert 'class="ota-scaled ota-shift"' in svg

    def test_draws_both_halves_with_labels_and_tooltips(self) -> None:
        svg = ring(backward_tooltip="Back", forward_tooltip="Forward").to_svg()

        assert 'id="ring-backward"' in svg
        assert 'id="ring-forward"' in svg
        assert ">◀1</text>" in svg
        assert ">3▶</text>" in svg
        assert "<title>Back</title>" in svg
        assert "<title>Forward</title>" in svg

    def test_skips_unavailable_half(self) -> None:
        svg = ring(backward_label=None).to_svg()

        assert "ring-backward" not in svg
        assert "ring-forward" in svg

    def test_marks_the_hovered_half(self) -> None:
        assert 'class="half hovered"' not in ring().to_svg()
        forward = ring(hovered_forward=True).to_svg()
        assert forward.count('class="half hovered"') == 1
        assert 'id="ring-forward" class="half hovered"' in forward

    def test_markup_has_no_colors(self) -> None:
        svg = ring().to_svg()

        for attribute in ["fill=", "stroke=", "font-size="]:
            assert attribute not in svg
