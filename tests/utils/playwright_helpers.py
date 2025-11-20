from playwright.sync_api import Page

from OTAnalytics.application.resources.resource_manager import (
    ProjectKeys,
    ResourceManager,
)


def set_input_value(page: Page, selector: str, value: str) -> None:
    """Robustly set a value on an input and ensure NiceGUI backend receives it.

    Strategy:
    - Click, fill, press Enter to commit, and blur to trigger NiceGUI's value change.
    - Additionally set value via evaluate() and dispatch input/change as a fallback.
    """
    loc = page.locator(selector).first
    loc.wait_for(state="visible")
    try:
        loc.click()
    except Exception:
        pass
    try:
        loc.fill("")
        loc.fill(value)
        try:
            loc.press("Enter")
        except Exception:
            pass
    except Exception:
        # ignore fill issues, fallback to JS below
        pass
    # Fallback: ensure events are dispatched and element is blurred
    loc.evaluate(
        "(el, v) => {\n"
        "  el.value = v;\n"
        "  el.dispatchEvent(new Event('input', { bubbles: true }));\n"
        "  el.dispatchEvent(new Event('change', { bubbles: true }));\n"
        "  if (el.blur) el.blur();\n"
        "}",
        value,
    )
    # Give the backend a short moment to process the websocket event
    page.wait_for_timeout(50)


def fill_project_information(
    page: Page,
    resource_manager: ResourceManager,
    name: str = "Test Project",
    date_value: str = "2023-05-24",
    time_value: str = "06:00:00",
) -> None:
    """Fill the mandatory project information fields on the main page."""
    name_sel = f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_PROJECT_NAME)}"]'
    date_sel = f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_DATE)}"]'
    time_sel = f'[aria-label="{resource_manager.get(ProjectKeys.LABEL_START_TIME)}"]'
    set_input_value(page, name_sel, name)
    set_input_value(page, date_sel, date_value)
    set_input_value(page, time_sel, time_value)
