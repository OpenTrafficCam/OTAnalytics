from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from nicegui import ui

STYLESHEET = Path(__file__).with_name("otanalytics.css")
"""Styles of the web UI. Classes are prefixed with `ota-`."""

VALID_FIELD_CLASS = "otanalytics-valid-field"
"""Marks a form field whose input passed its validation."""

DATETIME_FIELD_CLASS = "ota-datetime-field"
DIALOG_CLASS = "ota-dialog"
WIDE_DIALOG_CLASS = "ota-dialog-wide"
STALE_CLASS = "ota-stale"
"""Dims what an out-of-date track assignment shows."""


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
    ui.button.default_props(add="no-caps")
    ui.checkbox.default_props("keep-color")
    ui.input.default_props("color=accent")
    ui.number.default_props("color=accent")
    ui.add_css(STYLESHEET)
    yield
