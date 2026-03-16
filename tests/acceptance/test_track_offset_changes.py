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
    click_slider_at_position,
    get_loaded_tracks_canvas_from_otconfig,
    load_main_page,
    wait_for_canvas_change,
)

# Ensure pytest-playwright is available; otherwise skip this module
playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


# Configure all tests in this module to run in headed mode
pytestmark = pytest.mark.headed


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

    # Get slider locators
    x_slider = page.locator(".q-slider__track-container").first
    y_slider = page.locator(".q-slider__track-container").nth(1)

    # Step 2: Change Offset X to 0.8 and verify
    before = canvas.screenshot()
    click_slider_at_position(page, x_slider, 0.8, PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
    wait_for_canvas_change(page, canvas, before)

    # Step 3: Change Offset Y to 0.8 and verify
    before = canvas.screenshot()
    click_slider_at_position(page, y_slider, 0.8, PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
    wait_for_canvas_change(page, canvas, before)

    # Step 4: Reset both offsets to 0.5 and verify
    before = canvas.screenshot()
    click_slider_at_position(page, x_slider, 0.5, PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
    click_slider_at_position(page, y_slider, 0.5, PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
    wait_for_canvas_change(page, canvas, before)

    # Step 5: Click "Show all tracks" to hide trajectories
    canvas_before_hide = canvas.screenshot()
    all_tracks_checkbox.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify no trajectories are shown (canvas should change)
    wait_for_canvas_change(page, canvas, canvas_before_hide)
