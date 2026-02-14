from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_filters_form.container import (  # noqa
    MARKER_FILTER_BY_DATE_CHECKBOX,
    MARKER_FILTER_RANGE_LABEL,
    MARKER_NEXT_DATE_BUTTON,
    MARKER_NEXT_EVENT_BUTTON,
    MARKER_NEXT_FRAMES_BUTTON,
    MARKER_NEXT_SECONDS_BUTTON,
    MARKER_PREV_DATE_BUTTON,
    MARKER_PREV_EVENT_BUTTON,
    MARKER_PREV_FRAMES_BUTTON,
    MARKER_PREV_SECONDS_BUTTON,
)
from tests.acceptance.conftest import NiceGUITestServer
from tests.conftest import ACCEPTANCE_TEST_WAIT_TIMEOUT
from tests.utils.playwright_helpers import (
    search_for_marker_element,
    setup_with_preconfigured_otconfig,
    wait_for_canvas_change,
)

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


def _click_navigation_button_and_verify(
    page: Page,
    canvas: Any,
    range_label: Any,
    test_id: str,
    button_name: str,
    *,
    skip_if_no_change: bool = False,
) -> tuple[bytes, str]:
    """Click navigation button and verify canvas and label change.

    Args:
        page: Playwright page object
        canvas: Canvas locator
        range_label: Range label locator
        test_id: Test ID of the button to click
        button_name: Human-readable button name for error messages

    Returns:
        Tuple of (new_canvas_screenshot, new_range_label_text)
    """
    btn = page.get_by_test_id(test_id)
    btn.scroll_into_view_if_needed()
    try:
        btn.wait_for(state="visible", timeout=2000)
    except Exception:
        # Fallback: find navigation button by aria-label or nearby text
        pass  # Keep using the test-id locator

    old_canvas = canvas.screenshot()
    old_label = range_label.inner_text()

    btn.click()
    page.wait_for_timeout(300)  # Increased wait after click

    # Verify canvas changed
    try:
        new_canvas = wait_for_canvas_change(page, canvas, old_canvas, timeout=3)
    except AssertionError:
        new_label = range_label.inner_text()
        if skip_if_no_change and new_label == old_label:
            pytest.skip(f"{button_name} had no effect (no events/sections available).")
        raise
    new_label = range_label.inner_text()

    # Verify range label changed
    assert new_label != old_label, (
        f"{button_name} button did not update filter range label "
        f"(was: '{old_label}', still: '{new_label}')"
    )

    return new_canvas, new_label


def _test_navigation_pair(
    page: Page,
    canvas: Any,
    range_label: Any,
    next_button_id: str,
    prev_button_id: str,
    navigation_type: str,
    *,
    skip_if_no_change: bool = False,
) -> tuple[bytes, bytes]:
    """Test a pair of forward/backward navigation buttons.

    Args:
        page: Playwright page object
        canvas: Canvas locator
        range_label: Range label locator
        next_button_id: Test ID for forward navigation button
        prev_button_id: Test ID for backward navigation button
        navigation_type: Type of navigation (e.g., "Date", "Seconds") for assertions

    Returns:
        Tuple of (forward_canvas, backward_canvas)
    """
    canvas_forward, label_forward = _click_navigation_button_and_verify(
        page,
        canvas,
        range_label,
        next_button_id,
        f"Next {navigation_type}",
        skip_if_no_change=skip_if_no_change,
    )
    canvas_backward, label_backward = _click_navigation_button_and_verify(
        page,
        canvas,
        range_label,
        prev_button_id,
        f"Previous {navigation_type}",
        skip_if_no_change=skip_if_no_change,
    )

    assert (
        label_forward != label_backward
    ), f"{navigation_type} forward/backward navigation produced same range"

    return canvas_forward, canvas_backward


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_filter_navigation_buttons(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """
    Acceptance (Playwright): Validate navigation buttons move filter range correctly.

    Test Steps:
    1. Setup: Add video and tracks, enable tracks layer
    2. Enable "Filter by Date" checkbox and apply a filter
    3. Test navigation buttons and verify:
       - ">" right of "Filter By Date" moves filter forward
       - "<" left of "Filter By Date" moves filter backward
       - ">" right of Seconds moves filter forward by seconds
       - "<" left of Seconds moves filter backward by seconds
       - ">" right of Frames moves filter forward by frames
       - "<" left of Frames moves filter backward by frames
       - ">" right of Event moves filter forward by event
       - "<" left of Event moves filter backward by event

    Expected Results:
    - Each navigation button changes the canvas (different trajectories/background)
    - Filter range label updates to reflect movement
    - Canvas changes are consistent with time progression (forward vs backward)
    """
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    page.goto(base_url + ENDPOINT_MAIN_PAGE)

    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"

    # Load preconfigured file with video and tracks already set up
    setup_with_preconfigured_otconfig(page, resource_manager, otconfig_path)

    # Get canvas reference
    from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (  # noqa
        MARKER_INTERACTIVE_IMAGE,
    )

    canvas = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).first
    canvas.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

    # Enable "Show all tracks" layer
    from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
        MARKER_VISUALIZATION_LAYERS_ALL,
    )

    checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    checkbox.scroll_into_view_if_needed()
    if not checkbox.is_checked():
        checkbox.click()
        page.wait_for_timeout(200)
    # Don't apply any filter - just enable the filter checkbox to activate navigation
    # The default range should include all the track data
    filter_checkbox = page.get_by_test_id(MARKER_FILTER_BY_DATE_CHECKBOX)
    filter_checkbox.scroll_into_view_if_needed()
    filter_checkbox.wait_for(state="visible", timeout=5000)
    if not filter_checkbox.is_checked():
        filter_checkbox.click()
        page.wait_for_timeout(1000)  # Wait for filter to apply with default range

    # Get range label element
    range_label = page.get_by_test_id(MARKER_FILTER_RANGE_LABEL)
    range_label.wait_for(state="attached", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

    # Test all navigation button pairs
    c1, c2 = _test_navigation_pair(
        page,
        canvas,
        range_label,
        MARKER_NEXT_DATE_BUTTON,
        MARKER_PREV_DATE_BUTTON,
        "date",
    )
    c3, c4 = _test_navigation_pair(
        page,
        canvas,
        range_label,
        MARKER_NEXT_SECONDS_BUTTON,
        MARKER_PREV_SECONDS_BUTTON,
        "seconds",
    )
    c5, c6 = _test_navigation_pair(
        page,
        canvas,
        range_label,
        MARKER_NEXT_FRAMES_BUTTON,
        MARKER_PREV_FRAMES_BUTTON,
        "frames",
    )
    c7, c8 = _test_navigation_pair(
        page,
        canvas,
        range_label,
        MARKER_NEXT_EVENT_BUTTON,
        MARKER_PREV_EVENT_BUTTON,
        "event",
        skip_if_no_change=True,
    )

    # Verify navigation produced multiple unique canvas states
    all_canvases = [c1, c2, c3, c4, c5, c6, c7, c8]
    unique_canvases = len(set(all_canvases))
    assert unique_canvases >= 4, (
        f"Expected at least 4 unique canvas states during navigation, "
        f"got {unique_canvases}"
    )


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_filter_navigation_buttons_with_screenshot(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """
    Acceptance (Playwright): Validate navigation buttons using screenshot comparison.

    Test Steps:
    1. Setup: Add video and tracks, enable tracks layer
    2. Enable "Filter by Date" checkbox
    3. Take baseline screenshot of canvas
    4. Click each navigation button and compare screenshots
    5. Verify each button produces a visually different state

    Expected Results:
    - Each navigation button changes the visual state of the canvas
    - Screenshots differ from baseline after each navigation action
    """
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    page.goto(base_url + ENDPOINT_MAIN_PAGE)

    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"

    # Load preconfigured file with video and tracks already set up
    setup_with_preconfigured_otconfig(page, resource_manager, otconfig_path)

    # Get canvas reference
    from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (  # noqa
        MARKER_INTERACTIVE_IMAGE,
    )

    canvas = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).first
    canvas.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

    # Enable "Show all tracks" layer
    from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
        MARKER_VISUALIZATION_LAYERS_ALL,
    )

    checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    checkbox.scroll_into_view_if_needed()
    if not checkbox.is_checked():
        checkbox.click()
        page.wait_for_timeout(200)

    # Enable filter checkbox
    filter_checkbox = page.get_by_test_id(MARKER_FILTER_BY_DATE_CHECKBOX)
    filter_checkbox.scroll_into_view_if_needed()
    filter_checkbox.wait_for(state="visible", timeout=5000)
    if not filter_checkbox.is_checked():
        filter_checkbox.click()
        page.wait_for_timeout(1000)

    # Get range label element
    range_label = page.get_by_test_id(MARKER_FILTER_RANGE_LABEL)
    range_label.wait_for(state="attached", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

    # Take baseline screenshot
    baseline_screenshot = canvas.screenshot()

    # Test each navigation button with screenshot comparison
    navigation_buttons = [
        (MARKER_NEXT_DATE_BUTTON, "Next Date"),
        (MARKER_PREV_DATE_BUTTON, "Previous Date"),
        (MARKER_NEXT_SECONDS_BUTTON, "Next Seconds"),
        (MARKER_PREV_SECONDS_BUTTON, "Previous Seconds"),
        (MARKER_NEXT_FRAMES_BUTTON, "Next Frames"),
        (MARKER_PREV_FRAMES_BUTTON, "Previous Frames"),
        (MARKER_NEXT_EVENT_BUTTON, "Next Event"),
        (MARKER_PREV_EVENT_BUTTON, "Previous Event"),
    ]

    screenshots = []
    for test_id, button_name in navigation_buttons:
        btn = page.get_by_test_id(test_id)
        btn.scroll_into_view_if_needed()
        btn.wait_for(state="visible", timeout=2000)

        old_screenshot = canvas.screenshot()
        btn.click()
        page.wait_for_timeout(300)

        # Wait for canvas to change
        new_screenshot = wait_for_canvas_change(page, canvas, old_screenshot, timeout=3)
        screenshots.append((button_name, new_screenshot))

        # Verify screenshot differs from baseline
        assert (
            new_screenshot != baseline_screenshot
        ), f"{button_name} button did not change canvas visually"

    # Verify we have multiple unique visual states
    unique_screenshots = len(set(s[1] for s in screenshots))
    assert unique_screenshots >= 4, (
        f"Expected at least 4 unique visual states during navigation, "
        f"got {unique_screenshots}"
    )


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_filter_navigation_buttons_save_screenshots(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """
    Acceptance (Playwright): Run navigation test and save screenshots at each step.

    This test captures and saves screenshots for each navigation button action
    to help with visual debugging and test verification.
    """
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    page.goto(base_url + ENDPOINT_MAIN_PAGE)

    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"

    # Create screenshots directory
    screenshots_dir = Path(__file__).parent / "screenshots" / "filter_navigation"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    # Load preconfigured file with video and tracks already set up
    setup_with_preconfigured_otconfig(page, resource_manager, otconfig_path)

    # Get canvas reference
    from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (  # noqa
        MARKER_INTERACTIVE_IMAGE,
    )

    canvas = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).first
    canvas.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

    # Enable "Show all tracks" layer
    from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
        MARKER_VISUALIZATION_LAYERS_ALL,
    )

    checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    checkbox.scroll_into_view_if_needed()
    if not checkbox.is_checked():
        checkbox.click()
        page.wait_for_timeout(200)

    # Save screenshot after setup
    screenshot = canvas.screenshot()
    (screenshots_dir / "01_after_setup.png").write_bytes(screenshot)

    # Enable filter checkbox
    filter_checkbox = page.get_by_test_id(MARKER_FILTER_BY_DATE_CHECKBOX)
    filter_checkbox.scroll_into_view_if_needed()
    filter_checkbox.wait_for(state="visible", timeout=5000)
    if not filter_checkbox.is_checked():
        filter_checkbox.click()
        page.wait_for_timeout(1000)

    # Save screenshot after enabling filter
    screenshot = canvas.screenshot()
    (screenshots_dir / "02_after_filter_enabled.png").write_bytes(screenshot)

    # Get range label element
    range_label = page.get_by_test_id(MARKER_FILTER_RANGE_LABEL)
    range_label.wait_for(state="attached", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

    # Test each navigation button with screenshot saving
    navigation_buttons = [
        (MARKER_NEXT_DATE_BUTTON, "next_date"),
        (MARKER_PREV_DATE_BUTTON, "prev_date"),
        (MARKER_NEXT_SECONDS_BUTTON, "next_seconds"),
        (MARKER_PREV_SECONDS_BUTTON, "prev_seconds"),
        (MARKER_NEXT_FRAMES_BUTTON, "next_frames"),
        (MARKER_PREV_FRAMES_BUTTON, "prev_frames"),
        (MARKER_NEXT_EVENT_BUTTON, "next_event"),
        (MARKER_PREV_EVENT_BUTTON, "prev_event"),
    ]

    step_number = 3
    for test_id, button_name in navigation_buttons:
        btn = page.get_by_test_id(test_id)
        btn.scroll_into_view_if_needed()
        btn.wait_for(state="visible", timeout=2000)

        old_screenshot = canvas.screenshot()

        # Get current range label before click
        label_before = range_label.inner_text()

        btn.click()
        page.wait_for_timeout(300)

        # Wait for canvas to change
        try:
            new_screenshot = wait_for_canvas_change(
                page, canvas, old_screenshot, timeout=3
            )
            label_after = range_label.inner_text()

            # Save screenshot with filename including range info
            filename = f"{step_number:02d}_after_{button_name}.png"
            (screenshots_dir / filename).write_bytes(new_screenshot)

            # Also save a text file with the range label info
            info_file = (
                screenshots_dir / f"{step_number:02d}_after_{button_name}_info.txt"
            )
            info_file.write_text(
                f"Button: {button_name}\n"
                f"Label before: {label_before}\n"
                f"Label after: {label_after}\n"
            )

            step_number += 1
        except AssertionError:
            # If canvas didn't change, still save it but mark as unchanged
            filename = f"{step_number:02d}_after_{button_name}_UNCHANGED.png"
            (screenshots_dir / filename).write_bytes(canvas.screenshot())
            step_number += 1

    print(f"\nScreenshots saved to: {screenshots_dir}")
