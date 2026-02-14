from pathlib import Path

import pytest
from playwright.sync_api import Page  # type: ignore

from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    VisualizationLayersKeys,
    VisualizationOffsetSliderKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
    MARKER_VISUALIZATION_LAYERS_ALL,
)
from OTAnalytics.plugin_ui.visualization.visualization import (
    ALL,
    ASSIGNED_TO_FLOWS,
    INTERSECTING_SECTIONS,
    NOT_ASSIGNED_TO_FLOWS,
    NOT_INTERSECTING_SECTIONS,
)
from tests.acceptance.conftest import PLAYWRIGHT_VISIBLE_TIMEOUT_MS, NiceGUITestServer
from tests.utils.playwright_helpers import (
    capture_and_verify_baseline,
    enable_all_tracks_layer,
    enable_and_apply_date_filter,
    get_loaded_tracks_canvas_from_otconfig,
    get_test_files_from_data_dir,
    navigate_to_main_page_with_url,
    reset_date_filter,
    setup_tracks_display,
    verify_canvas_matches_reference,
    verify_filter_active,
    verify_filter_inactive,
    verify_filter_range_label_cleared,
    verify_filter_range_label_visible,
    wait_for_canvas_change,
)

SCREENSHOT_PATH = "screenshots"
ALL_TRACKS_FILE_NAME = "all_tracks.png"

# Ensure pytest-playwright is available; otherwise skip this module
playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)

# Timing constants (milliseconds)
UI_PROCESSING_GRACE_PERIOD_MS = 150
FILTER_APPLY_WAIT_MS = 200


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_add_tracks_and_display_all(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """Acceptance (Playwright): Add tracks and display all trajectories.

    Test Steps:
    1. Add a video file (prerequisite for tracks display)
    2. Navigate to Tracks tab
    3. Add track files via the in-app file picker
    4. Enable "Show all tracks" layer
    5. Verify trajectories are displayed on canvas

    Expected Results:
    - Track file loads without error
    - Canvas shows track trajectories when layer is enabled
    - Canvas image changes after enabling the tracks layer
    """
    # Setup
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    navigate_to_main_page_with_url(page, base_url)
    data_dir = Path(__file__).parents[1] / "data"
    video_file, track_files = get_test_files_from_data_dir(data_dir)

    # Take baseline before enabling tracks layer
    canvas = setup_tracks_display(
        page, resource_manager, video_file, track_files, enable_tracks_layer=False
    )
    canvas_before_tracks = canvas.screenshot()

    # Enable "Show all tracks" layer
    enable_all_tracks_layer(page)

    # Verify trajectories are displayed (canvas changed)
    canvas_with_tracks = wait_for_canvas_change(page, canvas, canvas_before_tracks)
    assert (
        canvas_with_tracks != canvas_before_tracks
    ), "Canvas did not change after enabling tracks layer - tracks not displayed"


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_filter_tracks_by_date(
    page: Page,
    external_app: NiceGUITestServer,
    acceptance_test_data_folder: Path,
    actual_screenshot_path: Path,
    resource_manager: ResourceManager,
) -> None:
    """Acceptance (Playwright): Filter displayed tracks by date range.

    Test Steps:
    1. Setup: Add video and tracks, enable tracks layer
    2. Enable "Filter by Date" checkbox
    3. Open filter dialog
    4. Set shorter time period (start time = end time for minimal range)
    5. Apply filter
    6. Verify filter is active
    7. Verify canvas updates (showing fewer/shorter trajectories)
    8. Verify background image shows filter end time

    Expected Results:
    - Filter can be activated and configured
    - Canvas updates to show filtered tracks
    - Filtered view shows fewer/shorter trajectories than unfiltered
    - Background image corresponds to filter end time

    Note: Requires reference screenshots to be generated first by running
    test_generate_canvas_screenshots.
    """
    # Setup: Load tracks with preconfigured file
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    navigate_to_main_page_with_url(page, base_url)
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"
    canvas = get_loaded_tracks_canvas_from_otconfig(
        page, resource_manager, otconfig_path
    )

    # Capture baseline and verify against reference
    reference_screenshot = acceptance_test_data_folder / ALL_TRACKS_FILE_NAME
    canvas_with_all_tracks = capture_and_verify_baseline(
        page, canvas, actual_screenshot_path, reference_screenshot
    )

    # Apply date filter
    enable_and_apply_date_filter(page, use_minimal_range=True)

    # Verify filter is active and range label is displayed
    verify_filter_active(page)
    verify_filter_range_label_visible(page)

    # Verify canvas updates to show filtered tracks
    canvas_with_filtered_tracks = wait_for_canvas_change(
        page, canvas, canvas_with_all_tracks
    )

    assert (
        canvas_with_filtered_tracks != canvas_with_all_tracks
    ), "Canvas did not update after applying date filter - filter not working"


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_toggle_intersection_layers(
    page: Page,
    external_app: NiceGUITestServer,
    acceptance_test_data_folder: Path,
    resource_manager: ResourceManager,
) -> None:
    """Verify that intersection layers can be toggled and canvas is loaded correctly.

    Note: Requires reference screenshots to be generated first by running
    test_generate_canvas_screenshots.
    """
    # Setup: Load tracks with preconfigured file
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    navigate_to_main_page_with_url(page, base_url)
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"
    canvas = get_loaded_tracks_canvas_from_otconfig(
        page, resource_manager, otconfig_path
    )
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Capture screenshot and verify against reference
    verify_canvas_matches_reference(
        canvas, acceptance_test_data_folder, ALL_TRACKS_FILE_NAME
    )


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_generate_canvas_screenshots(
    external_app: NiceGUITestServer,
    page: Page,
    resource_manager: ResourceManager,
    acceptance_test_data_folder: Path,
) -> None:
    """Generate reference screenshots for all visualization layer states."""
    # Setup: Load tracks with preconfigured file
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    navigate_to_main_page_with_url(page, base_url)
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"
    canvas = get_loaded_tracks_canvas_from_otconfig(
        page, resource_manager, otconfig_path
    )

    # Helper function to toggle a checkbox and take screenshot
    def toggle_and_screenshot(
        checkbox_text: str, filename_base: str, nth: int = 0
    ) -> None:
        """Toggle a checkbox on, take screenshot, then toggle off.

        Args:
            checkbox_text: Text of the checkbox to find
            filename_base: Base name for screenshot files
            nth: Which occurrence to use if multiple checkboxes have same text
        """
        checkbox = page.get_by_text(checkbox_text, exact=True).nth(nth)
        checkbox.scroll_into_view_if_needed()

        # Toggle on and screenshot
        if not checkbox.is_checked():
            checkbox.click()
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
        canvas.screenshot(path=acceptance_test_data_folder / f"{filename_base}.png")

        # Toggle off (no screenshot)
        checkbox.click()
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # 1. Show all tracks (already enabled, just take screenshot)
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
    canvas.screenshot(path=acceptance_test_data_folder / ALL_TRACKS_FILE_NAME)

    # Sections and flows are already loaded from the preconfigured file
    # Just update flow highlighting
    page.get_by_text(
        resource_manager.get(VisualizationLayersKeys.BUTTON_UPDATE_FLOW_HIGHLIGHTING),
        exact=True,
    ).click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Turn off "Show all tracks" to prepare for next screenshots
    all_tracks_checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    all_tracks_checkbox.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # 2. Show offset ändern und zurücksetzen (Update with section offset button)
    # This button may be disabled if preconditions aren't met, so skip if not enabled
    offset_button = page.get_by_text(
        resource_manager.get(VisualizationOffsetSliderKeys.BUTTON_UPDATE_OFFSET),
        exact=True,
    )
    if offset_button.count() > 0:
        offset_button.scroll_into_view_if_needed()
        canvas.screenshot(path=acceptance_test_data_folder / "offset_before.png")
        # Only click if enabled
        if not offset_button.is_disabled():
            offset_button.click()
            page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
            canvas.screenshot(path=acceptance_test_data_folder / "offset_after.png")

    # 3-11. Toggle all visualization layers and take screenshots
    # Deselect "Show all tracks" before testing individual highlight options
    all_tracks_checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    if all_tracks_checkbox.is_checked():
        all_tracks_checkbox.click()
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Show tracks group (nth=0 means first occurrence in "Show tracks" section)
    toggle_and_screenshot(
        INTERSECTING_SECTIONS, "highlight_tracks_intersecting_sections", nth=0
    )
    toggle_and_screenshot(
        NOT_INTERSECTING_SECTIONS, "highlight_tracks_not_intersecting_sections", nth=0
    )
    toggle_and_screenshot(
        ASSIGNED_TO_FLOWS, "highlight_tracks_assigned_to_flows", nth=0
    )
    toggle_and_screenshot(
        NOT_ASSIGNED_TO_FLOWS, "highlight_tracks_not_assigned_to_flows", nth=0
    )

    # Show start and end points group
    # (nth=1 means second occurrence in "Show start and end points" section)
    toggle_and_screenshot(
        INTERSECTING_SECTIONS, "start_end_intersecting_sections", nth=1
    )
    toggle_and_screenshot(
        NOT_INTERSECTING_SECTIONS, "start_end_not_intersecting_sections", nth=1
    )
    toggle_and_screenshot(ALL, "start_end_all", nth=1)
    toggle_and_screenshot(ASSIGNED_TO_FLOWS, "start_end_assigned_to_flows", nth=1)
    toggle_and_screenshot(
        NOT_ASSIGNED_TO_FLOWS, "start_end_not_assigned_to_flows", nth=1
    )


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_reset_track_filter(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """Acceptance (Playwright): Reset track date filter to show all tracks again.

    Test Steps:
    1. Setup: Add video, tracks, enable tracks layer, apply date filter
    2. Open filter dialog
    3. Click Reset button
    4. Verify filter is deactivated
    5. Verify filter range label is cleared

    Expected Results:
    - Reset button clears the date filter
    - Filter button shows inactive state
    - Range label is empty after reset
    """
    # Setup: Load tracks and apply date filter
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    navigate_to_main_page_with_url(page, base_url)
    data_dir = Path(__file__).parents[1] / "data"
    video_file, track_files = get_test_files_from_data_dir(data_dir)
    setup_tracks_display(
        page, resource_manager, video_file, track_files, enable_tracks_layer=True
    )
    enable_and_apply_date_filter(page, use_minimal_range=True)

    # Verify filter is active before reset
    verify_filter_active(page)

    # Reset filter
    reset_date_filter(page)

    # Verify filter is deactivated and range label is cleared
    verify_filter_inactive(page)
    verify_filter_range_label_cleared(page)
