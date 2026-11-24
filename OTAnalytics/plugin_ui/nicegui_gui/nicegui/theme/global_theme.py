from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from nicegui import app, ui

STYLESHEET = Path(__file__).with_name("otanalytics.css")
"""Styles of the web UI. Classes are prefixed with `ota-`."""

FONTS_DIR = Path(__file__).with_name("fonts")
FONTS_ROUTE = "/ota-fonts"
"""Where the bundled fonts are served, as the stylesheet expects them."""

VALID_FIELD_CLASS = "otanalytics-valid-field"
"""Marks a form field whose input passed its validation."""

DATETIME_FIELD_CLASS = "ota-datetime-field"
DATE_FIELD_CLASS = "ota-date-field"
DIALOG_CLASS = "ota-dialog"
WIDE_DIALOG_CLASS = "ota-dialog-wide"
STALE_CLASS = "ota-stale"
"""Dims what an out-of-date track assignment shows."""


def add_fonts() -> None:
    """Serve the bundled fonts, so the web UI needs no internet connection."""
    app.add_static_files(FONTS_ROUTE, FONTS_DIR)


@contextmanager
def global_theme() -> Generator[None, None, None]:
    # The primary colour is defined in the stylesheet.
    ui.colors(
        secondary="#97D5E0",
        accent="#70A9A1",
        background="#F5F5F5",
        surface="#FFFFFF",
        text_primary="#333333",
        text_secondary="#757575",
        error="#E60000",
        info="#4A90E2",
    )
    # Compact desktop density; sizes are set in the stylesheet.
    ui.button.default_props(add="no-caps unelevated dense")
    ui.checkbox.default_props("keep-color dense")
    ui.switch.default_props("dense")
    ui.input.default_props("color=accent outlined dense")
    ui.number.default_props("color=accent outlined dense")
    ui.select.default_props("outlined dense")
    ui.tabs.default_props("dense")
    ui.table.default_props("dense flat bordered")
    ui.add_css(STYLESHEET)
    yield
