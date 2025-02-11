from contextlib import contextmanager
from typing import Generator

from nicegui import ui


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
    yield
