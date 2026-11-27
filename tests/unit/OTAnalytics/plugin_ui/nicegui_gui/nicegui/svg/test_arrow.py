from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.arrow import Arrow
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.line_resources import LineResources


def create_arrow(count: int | None = 7) -> Arrow:
    return Arrow(id="arrow-a-b", x1=0, y1=0, x2=100, y2=0, count=count)


class TestArrow:
    def test_control_point_is_left_of_direction(self) -> None:
        assert create_arrow().control_point() == (50, -12)

    def test_point_at_half(self) -> None:
        assert create_arrow().point_at(0.5) == (50, -6)

    def test_markup(self) -> None:
        svg = create_arrow().to_svg()

        assert svg.startswith('<g id="arrow-a-b" class="ota-flow">')
        assert '<path class="casing" d="M0 0 Q50 -12 100 0"/>' in svg
        assert '<path class="line" d="M0 0 Q50 -12 100 0"/>' in svg
        assert (
            '<g transform="translate(100 0) rotate(13.5)"><g class="ota-scaled">'
            '<polygon class="head" points="0,0 -12,-5 -12,5"/></g></g>'
        ) in svg
        assert (
            '<g transform="translate(50 -6)"><g class="ota-scaled ota-badge">'
            '<rect x="-11.5" y="-10" width="23" height="20" rx="10"/>'
            '<text y="4">7</text></g></g>'
        ) in svg
        assert "stroke=" not in svg
        assert "fill=" not in svg

    def test_stale(self) -> None:
        assert (
            create_arrow()
            .to_svg(stale=True)
            .startswith('<g id="arrow-a-b" class="ota-flow stale">')
        )

    def test_without_count_has_no_badge(self) -> None:
        assert "ota-badge" not in create_arrow(count=None).to_svg()


class TestLineResources:
    def test_passes_stale_to_arrows(self) -> None:
        resources = LineResources({})
        arrow = create_arrow()
        resources.add(arrow)

        assert resources.to_svg(stale=True) == arrow.to_svg(stale=True)
        resources.clear()
        assert resources.to_svg() == ""
