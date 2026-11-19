"""Tests that the stylesheet defines every class the web UI uses."""

import re
from pathlib import Path
from unittest.mock import patch

from nicegui import ui
from nicegui.testing import User

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.theme.global_theme import (
    STYLESHEET,
    VALID_FIELD_CLASS,
    global_theme,
)

PRIMARY_COLOR = "#37483e"
NICEGUI_GUI = Path(STYLESHEET).parents[2]
CLASS_IN_PYTHON = re.compile(r"""["' ](ota-[a-z-]+)""")
CLASS_IN_CSS = re.compile(r"\.(ota-[a-z-]+|otanalytics-[a-z-]+)")


def classes_used_in_python() -> set[str]:
    return {
        match
        for path in NICEGUI_GUI.rglob("*.py")
        for match in CLASS_IN_PYTHON.findall(path.read_text(encoding="utf-8"))
    }


def classes_defined_in_css() -> set[str]:
    return set(CLASS_IN_CSS.findall(Path(STYLESHEET).read_text(encoding="utf-8")))


class TestStylesheet:
    def test_defines_every_class_used_in_the_web_ui(self) -> None:
        used = classes_used_in_python()

        assert used, "the web ui uses no stylesheet class"
        assert used <= classes_defined_in_css()

    def test_defines_the_valid_field_style(self) -> None:
        assert VALID_FIELD_CLASS in classes_defined_in_css()

    def test_defines_the_panel_widths_as_tokens(self) -> None:
        css = Path(STYLESHEET).read_text(encoding="utf-8")

        assert "--ota-left-width: 344px" in css
        assert "--ota-right-width: 288px" in css

    async def test_is_loaded_by_the_theme(self, user: User) -> None:
        @ui.page("/test-global-theme")
        def page() -> None:
            with global_theme():
                ui.label("themed")

        await user.open("/test-global-theme")

        assert user.client is not None
        assert ".ota-left" in user.client.head_html

    def test_defines_the_primary_colour(self) -> None:
        """ui.colors() writes every colour inline on the body, so the stylesheet
        overrides it."""
        css = Path(STYLESHEET).read_text(encoding="utf-8")

        assert f"--ota-primary: {PRIMARY_COLOR}" in css
        assert "--q-primary: var(--ota-primary) !important" in css

    def test_leaves_the_primary_colour_to_the_stylesheet(self) -> None:
        with patch(
            "OTAnalytics.plugin_ui.nicegui_gui.nicegui.theme.global_theme.ui"
        ) as mock_ui:
            with global_theme():
                pass

        assert "primary" not in mock_ui.colors.call_args.kwargs


class TestDensity:
    async def test_controls_are_compact(self, user: User) -> None:
        @ui.page("/test-density")
        def page() -> None:
            with global_theme():
                ui.button("button").mark("button")
                ui.input("input").mark("input")
                ui.checkbox("checkbox").mark("checkbox")
                ui.table(columns=[], rows=[]).mark("table")

        await user.open("/test-density")

        def props(marker: str) -> dict:
            return user.find(marker=marker).elements.pop().props

        assert {"dense", "unelevated", "no-caps"} <= set(props("button"))
        assert {"dense", "outlined"} <= set(props("input"))
        assert "dense" in props("checkbox")
        assert {"dense", "flat", "bordered"} <= set(props("table"))

    def test_uses_the_design_palette(self) -> None:
        css = Path(STYLESHEET).read_text(encoding="utf-8")

        for token in (
            "--ota-primary: #37483e",
            "--ota-text-muted: #596d63",
            "--ota-border: #d9e2dd",
            "--ota-border-strong: #b4c2bb",
            "--ota-bg: #f6f8f7",
            "--ota-selected: #d4e1da",
            "--nicegui-default-gap: 8px",
        ):
            assert token in css, token
