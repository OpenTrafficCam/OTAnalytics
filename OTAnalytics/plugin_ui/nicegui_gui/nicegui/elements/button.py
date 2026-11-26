from typing import Any, Callable

from nicegui import ui
from nicegui.elements.button import Button

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import (
    LazyInitializedElement,
)
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID


class CustomButton(LazyInitializedElement[Button]):
    """A button of the design.

    Primary buttons are filled with the primary colour, which is the default of
    every button. Secondary buttons are outlined.

    Args:
        text (str): Label of the button.
        on_click (Callable[..., Any]): Called when the button is clicked.
        marker (str | None): Marker to identify the button in tests, also exposed
            as test id to browser tests. Defaults to None.
        secondary (bool): Outline the button instead of filling it. Defaults to
            False.
        icon (str | None): Icon in front of the label. Defaults to None.
    """

    def __init__(
        self,
        text: str,
        on_click: Callable[..., Any],
        marker: str | None = None,
        secondary: bool = False,
        icon: str | None = None,
    ) -> None:
        super().__init__()
        self._text = text
        self._on_click = on_click
        self._marker = marker
        self._secondary = secondary
        self._icon = icon

    def build(self) -> Button:
        """Build the NiceGUI button.

        Returns:
            Button: The built button, e.g. to enable or disable it.
        """
        self._instance = ui.button(self._text, icon=self._icon, on_click=self._on_click)
        if self._secondary:
            self._instance.props("outline")
        if self._marker:
            self._instance.mark(self._marker)
            self._instance.props(f"{TEST_ID}={self._marker}")
        return self._instance
