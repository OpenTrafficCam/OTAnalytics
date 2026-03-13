"""Acceptance tests for track offset functionality.

This test verifies that track offset can be changed via X/Y sliders
and that tracks are repositioned accordingly on the canvas.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
    MARKER_VISUALIZATION_LAYERS_ALL,
)
from tests.acceptance.conftest import PLAYWRIGHT_VISIBLE_TIMEOUT_MS, NiceGUITestServer
from tests.utils.playwright_helpers import (
    get_loaded_tracks_canvas_from_otconfig,
    load_main_page,
    wait_for_canvas_change,
)

# Ensure pytest-playwright is available; otherwise skip this module
playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)

# Timing constants (milliseconds)
UI_PROCESSING_GRACE_PERIOD_MS = 150


@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_track_offset_x_and_y_changes(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """Acceptance (Playwright): Change track offset X and Y values and verify display.

    Test Steps:
    1. Load tracks with preconfigured file
    2. Click "Show all tracks" to display trajectories
    3. Change Offset X to 0.8 and verify canvas updates
    4. Change Offset Y to 0.8 and verify canvas updates
    5. Reset offset to X: 0.5, Y: 0.5 and verify canvas updates
    6. Click "Show all tracks" again to hide trajectories

    Expected Results:
    - Tracks are displayed when "Show all tracks" is enabled
    - Changing X offset moves tracks horizontally
    - Changing Y offset moves tracks vertically
    - Resetting offset to 0.5/0.5 returns tracks to center position
    - Clicking "Show all tracks" again hides trajectories
    """
    # Setup: Load tracks with preconfigured file
    load_main_page(page, external_app)
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"
    canvas = get_loaded_tracks_canvas_from_otconfig(
        page, resource_manager, otconfig_path
    )

    # Step 1: Show all tracks
    all_tracks_checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)

    # Ensure tracks are visible first
    if not all_tracks_checkbox.is_checked():
        all_tracks_checkbox.click()
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    canvas_with_all_tracks = canvas.screenshot()

    # Step 2: Change Offset X to 0.8
    canvas_before_x_change = canvas.screenshot()

    # Locate X slider (first slider on the page)
    x_slider_track = page.locator(".q-slider__track-container").first
    x_slider_track.scroll_into_view_if_needed()

    # Click at 80% position on the slider track to set value to 0.8
    bbox = x_slider_track.bounding_box()
    if bbox:
        x_slider_track.click(
            position={"x": bbox["width"] * 0.8, "y": bbox["height"] / 2}
        )
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify canvas changed after X offset change
    wait_for_canvas_change(page, canvas, canvas_before_x_change)

    # Step 3: Change Offset Y to 0.8
    canvas_before_y_change = canvas.screenshot()

    # Locate Y slider (second slider on the page)
    y_slider_track = page.locator(".q-slider__track-container").nth(1)
    y_slider_track.scroll_into_view_if_needed()

    # Click at 80% position on the slider track to set value to 0.8
    bbox = y_slider_track.bounding_box()
    if bbox:
        y_slider_track.click(
            position={"x": bbox["width"] * 0.8, "y": bbox["height"] / 2}
        )
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify canvas changed after Y offset change
    wait_for_canvas_change(page, canvas, canvas_before_y_change)

    # Step 4: Reset offset to X: 0.5, Y: 0.5
    canvas_before_reset = canvas.screenshot()

    # Reset X to 0.5 (click at 50% position)
    bbox = x_slider_track.bounding_box()
    if bbox:
        x_slider_track.click(
            position={"x": bbox["width"] * 0.5, "y": bbox["height"] / 2}
        )
    page.wait_for_timeout(UI_PROCESSING_GRACE_PERIOD_MS)

    # Reset Y to 0.5 (click at 50% position)
    bbox = y_slider_track.bounding_box()
    if bbox:
        y_slider_track.click(
            position={"x": bbox["width"] * 0.5, "y": bbox["height"] / 2}
        )
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify canvas changed after reset
    wait_for_canvas_change(page, canvas, canvas_before_reset)

    # Step 5: Click "Show all tracks" to hide trajectories
    all_tracks_checkbox.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify no trajectories are shown
    wait_for_canvas_change(page, canvas, canvas_with_all_tracks)
