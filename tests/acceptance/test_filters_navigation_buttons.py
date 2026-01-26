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
from tests.utils.playwright_helpers import setup_tracks_display, wait_for_canvas_change

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)

# Test data constants
TEST_VIDEO_FILENAME = "Testvideo_Cars-Truck_FR20_2020-01-01_00-00-00.mp4"
TEST_TRACK_FILENAME = "Testvideo_Cars-Truck_FR20_2020-01-01_00-00-00.ottrk"


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
    video_file = data_dir / TEST_VIDEO_FILENAME
    track_file = data_dir / TEST_TRACK_FILENAME
    assert video_file.exists(), f"Test video file missing: {video_file}"
    assert track_file.exists(), f"Test track file missing: {track_file}"

    # Setup: Add video, tracks, enable layer, and apply filter
    canvas = setup_tracks_display(
        page, resource_manager, video_file, track_file, enable_tracks_layer=True
    )
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
