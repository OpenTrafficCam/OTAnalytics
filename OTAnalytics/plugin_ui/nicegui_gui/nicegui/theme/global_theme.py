from contextlib import contextmanager
from typing import Generator

from nicegui import ui

VALID_FIELD_CLASS = "otanalytics-valid-field"
"""Marks a form field whose input passed its validation."""

# Draws the underline like Quasar draws it for an error, but green.
VALID_FIELD_CSS = f"""
.q-field.{VALID_FIELD_CLASS} .q-field__control:after {{
    background: var(--q-positive);
    transform: scale3d(1, 1, 1);
}}
.q-field.{VALID_FIELD_CLASS} .q-field__label {{
    color: var(--q-positive);
}}
"""


@contextmanager
def global_theme() -> Generator[None, None, None]:
    ui.colors(
        primary="#415841",
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
    ui.add_css(VALID_FIELD_CSS)
    yield
