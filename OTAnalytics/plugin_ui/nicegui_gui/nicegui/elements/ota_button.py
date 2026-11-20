from typing import Any, Callable

from nicegui import ui

from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID


def ota_button(
    text: str,
    on_click: Callable[..., Any],
    marker: str,
    secondary: bool = False,
    icon: str | None = None,
    test_id: bool = False,
) -> ui.button:
    """Create a button of the design.

    Primary buttons are filled with the primary colour, which is the default
    of every button. Secondary buttons are outlined.

    Args:
        text: label of the button.
        on_click: called when the button is clicked.
        marker: marks the button for tests.
        secondary: outline the button instead of filling it.
        icon: icon in front of the label.
        test_id: also expose the marker to browser tests. Only one element of
            the page should carry a test id.
    """
    button = ui.button(text, icon=icon, on_click=on_click)
    if secondary:
        button.props("outline")
    button.mark(marker)
    if test_id:
        button.props(f"{TEST_ID}={marker}")
    return button
