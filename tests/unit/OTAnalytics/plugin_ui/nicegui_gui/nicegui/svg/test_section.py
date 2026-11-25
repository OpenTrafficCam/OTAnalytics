from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import dot
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.section import SectionShape
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.section_resources import (
    SectionResource,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.text import Text


class TestText:
    def test_chip(self) -> None:
        svg = Text(x=5, y=30, text="North").to_svg()

        assert svg == (
            '<g transform="translate(5 30)"><g class="ota-scaled ota-chip">'
            '<g transform="translate(8 -30)">'
            '<rect width="51" height="22" rx="6"/>'
            '<text x="8" y="15">North</text></g></g></g>'
        )

    def test_chip_escapes_name(self) -> None:
        svg = Text(x=0, y=0, text="<b>&").to_svg()

        assert "&lt;b&gt;&amp;" in svg
        assert "<b>" not in svg
        assert 'width="44"' in svg


class TestSectionShape:
    def test_line_section(self) -> None:
        svg = SectionShape(id="s", points=[(0, 0), (10, 0)]).to_svg()

        assert svg.startswith('<g id="s" class="ota-section">')
        assert svg.endswith("</g>")
        for part in ["glow", "casing", "line"]:
            assert f'<polyline class="{part}" points="0,0 10,0"/>' in svg
        assert dot(0, 0, "pt-ring") in svg
        assert dot(0, 0, "pt", "s-0") in svg
        assert dot(10, 0, "pt", "s-1") in svg
        assert "<text" not in svg

    def test_area_section(self) -> None:
        svg = SectionShape(
            id="a", points=[(0, 0), (10, 0), (10, 10)], is_area=True, selected=True
        ).to_svg()

        assert svg.startswith('<g id="a" class="ota-section area selected">')
        assert '<polygon class="line" points="0,0 10,0 10,10"/>' in svg

    def test_editing_section_without_points(self) -> None:
        svg = SectionShape(
            id="s-edit", points=[(0, 0), (10, 0)], editing=True, show_points=False
        ).to_svg()

        assert svg.startswith('<g id="s-edit" class="ota-section editing">')
        assert "pt" not in svg

    def test_chip_at_first_point_of_line(self) -> None:
        svg = SectionShape(id="s", points=[(5, 30), (10, 0)], name="North").to_svg()

        assert Text(x=5, y=30, text="North").to_svg() in svg

    def test_chip_at_centroid_of_area(self) -> None:
        svg = SectionShape(
            id="a", points=[(0, 0), (30, 0), (0, 30)], is_area=True, name="Area"
        ).to_svg()

        assert 'transform="translate(10 10)"' in svg

    def test_id_is_escaped(self) -> None:
        svg = SectionShape(id='a"b', points=[(0, 0)]).to_svg()

        assert 'id="a&quot;b"' in svg


class TestSectionResource:
    def test_add_and_clear(self) -> None:
        resource = SectionResource({})
        first = SectionShape(id="1", points=[(0, 0), (1, 1)])
        second = SectionShape(id="2", points=[(2, 2), (3, 3)])

        resource.add(first)
        resource.add(second)

        assert resource.to_svg() == first.to_svg() + second.to_svg()
        resource.clear()
        assert resource.to_svg() == ""


class TestKnobNumber:
    def test_knob_shows_its_position_inside(self) -> None:
        from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.knob import Knob

        svg = Knob(index=2, x=10, y=20).to_svg()

        assert '<text class="num">3</text>' in svg
        assert '<g transform="translate(10 20)">' in svg
        assert svg.index("num") < svg.index("edit-knob-2")
