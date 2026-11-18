from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.text import Text


class TestText:
    def test_text_to_svg(self) -> None:
        text = Text(id="section-text", x=10, y=20, text="North", color="green")

        svg = text.to_svg()

        assert "<text" in svg
        assert 'id="section-text"' in svg
        assert 'x="10"' in svg
        assert 'y="20"' in svg
        assert 'fill="green"' in svg
        assert ">North</text>" in svg

    def test_text_is_escaped(self) -> None:
        text = Text(id="section-text", x=10, y=20, text="<b>&</b>", color="green")

        svg = text.to_svg()

        assert "&lt;b&gt;&amp;&lt;/b&gt;" in svg
        assert "<b>" not in svg
