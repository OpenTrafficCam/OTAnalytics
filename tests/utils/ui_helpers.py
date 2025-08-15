from typing import Any

from nicegui.testing import Screen


def set_input_value(screen: Screen, element: Any, value: str) -> None:
    """Set the value of an input element via Selenium JS and dispatch events.

    This mirrors real user typing by updating the value property and emitting
    both 'input' and 'change' events, which many UI frameworks rely on.

    Args:
        screen: NiceGUI Screen fixture providing selenium driver
        element: The web element to update (result of find/find_by_css, etc.)
        value: The value to set on the element
    """
    screen.selenium.execute_script("arguments[0].value = arguments[1];", element, value)
    screen.selenium.execute_script(
        "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
        element,
    )
    screen.selenium.execute_script(
        "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
        element,
    )
