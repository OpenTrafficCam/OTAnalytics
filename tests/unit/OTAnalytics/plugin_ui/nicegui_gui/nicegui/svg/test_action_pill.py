from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.action_pill import \
    ActionPill


class TestActionPill:
    def test_has_ids_for_each_part(self) -> None:
        pill = ActionPill(id="pill", x=100, y=50)

        assert pill.finish_id == "pill-finish"
        assert pill.cancel_id == "pill-cancel"
        assert pill.background_id == "pill-background"

    def test_draws_both_buttons_with_tooltips(self) -> None:
        svg = ActionPill(
            id="pill", x=100, y=50, finish_tooltip="Finish", cancel_tooltip="Cancel"
        ).to_svg()

        assert 'id="pill-finish"' in svg
        assert 'id="pill-cancel"' in svg
        assert "<title>Finish</title>" in svg
        assert "<title>Cancel</title>" in svg

    def test_finish_button_is_left_of_cancel_button(self) -> None:
        svg = ActionPill(id="pill", x=100, y=50).to_svg()

        assert svg.index("pill-finish") < svg.index("pill-cancel")

    def test_disabled_finish_button_is_marked(self) -> None:
        assert "ota-action-disabled" not in ActionPill(id="p", x=0, y=0).to_svg()
        assert (
            "ota-action-disabled"
            in ActionPill(id="p", x=0, y=0, finish_enabled=False).to_svg()
        )

    def test_escapes_tooltips(self) -> None:
        svg = ActionPill(id="p", x=0, y=0, finish_tooltip="<b>").to_svg()

        assert "<title>&lt;b&gt;</title>" in svg
