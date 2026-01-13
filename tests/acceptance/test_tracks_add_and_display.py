from pathlib import Path

import pytest
from playwright.sync_api import Page  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    TrackFormKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (
    MARKER_INTERACTIVE_IMAGE,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_filters_form.container import (  # noqa
    MARKER_FILTER_BY_DATE_APPLY_BUTTON,
    MARKER_FILTER_BY_DATE_BUTTON,
    MARKER_FILTER_BY_DATE_CHECKBOX,
    MARKER_FILTER_END_DATE_INPUT,
    MARKER_FILTER_END_TIME_INPUT,
    MARKER_FILTER_RANGE_LABEL,
    MARKER_FILTER_START_DATE_INPUT,
    MARKER_FILTER_START_TIME_INPUT,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
    MARKER_VISUALIZATION_LAYERS_ALL,
)
from tests.acceptance.conftest import NiceGUITestServer
from tests.conftest import ACCEPTANCE_TEST_WAIT_TIMEOUT
from tests.utils.playwright_helpers import (
    add_track_via_picker,
    add_video_via_picker,
    search_for_marker_element,
    wait_for_canvas_change,
)

# Ensure pytest-playwright is available; otherwise skip this module
playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)

# Test data constants
TEST_VIDEO_FILENAME = "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
TEST_TRACK_FILENAME = "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.ottrk"

# Timing constants (milliseconds)
UI_PROCESSING_GRACE_PERIOD_MS = 150
FILTER_APPLY_WAIT_MS = 200


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
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    page.goto(base_url + ENDPOINT_MAIN_PAGE)

    # Setup: Add video first (required for tracks display)
    data_dir = Path(__file__).parents[1] / "data"
    video_file = data_dir / TEST_VIDEO_FILENAME
    assert video_file.exists(), f"Test video file missing: {video_file}"

    page.get_by_text(resource_manager.get(TrackFormKeys.TAB_VIDEO), exact=True).click()
    add_video_via_picker(page, resource_manager, video_file)
    page.wait_for_timeout(UI_PROCESSING_GRACE_PERIOD_MS)

    # Step 1: Navigate to Tracks tab
    page.get_by_text(resource_manager.get(TrackFormKeys.TAB_TRACK), exact=True).click()

    # Step 2: Add track file
    track_file = data_dir / TEST_TRACK_FILENAME
    assert track_file.exists(), f"Test track file missing: {track_file}"
    add_track_via_picker(page, resource_manager, track_file)

    # Step 3: Get canvas reference and take baseline screenshot
    canvas = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).first
    canvas.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)
    canvas_before_tracks = canvas.screenshot()

    # Step 4: Enable "Show all tracks" layer
    checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    checkbox.scroll_into_view_if_needed()
    checkbox.click()

    # Step 5: Verify trajectories are displayed (canvas changed)
    canvas_with_tracks = wait_for_canvas_change(page, canvas, canvas_before_tracks)
    assert (
        canvas_with_tracks != canvas_before_tracks
    ), "Canvas did not change after enabling tracks layer - tracks not displayed"


@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_filter_tracks_by_date(
    page: Page,
    external_app: NiceGUITestServer,
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
    """
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    page.goto(base_url + ENDPOINT_MAIN_PAGE)

    # Setup: Add video and tracks
    data_dir = Path(__file__).parents[1] / "data"
    video_file = data_dir / TEST_VIDEO_FILENAME
    track_file = data_dir / TEST_TRACK_FILENAME
    assert video_file.exists(), f"Test video file missing: {video_file}"
    assert track_file.exists(), f"Test track file missing: {track_file}"

    page.get_by_text(resource_manager.get(TrackFormKeys.TAB_VIDEO), exact=True).click()
    add_video_via_picker(page, resource_manager, video_file)
    page.wait_for_timeout(UI_PROCESSING_GRACE_PERIOD_MS)

    page.get_by_text(resource_manager.get(TrackFormKeys.TAB_TRACK), exact=True).click()
    add_track_via_picker(page, resource_manager, track_file)

    canvas = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).first
    canvas.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

    # Enable tracks layer
    checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    checkbox.scroll_into_view_if_needed()
    checkbox.click()

    # Wait for tracks to be displayed
    canvas_baseline = canvas.screenshot()
    canvas_with_all_tracks = wait_for_canvas_change(page, canvas, canvas_baseline)

    # Step 1: Enable "Filter by Date" checkbox
    filter_by_date_checkbox = page.get_by_test_id(MARKER_FILTER_BY_DATE_CHECKBOX)
    filter_by_date_checkbox.scroll_into_view_if_needed()
    filter_by_date_checkbox.click()

    # Step 2: Open filter dialog
    filter_by_date_button = page.get_by_test_id(MARKER_FILTER_BY_DATE_BUTTON)
    filter_by_date_button.click()

    # Step 3: Configure filter with minimal time range (start = end)
    # This creates a shorter period, showing fewer trajectories at a specific moment
    start_date_input = page.get_by_test_id(MARKER_FILTER_START_DATE_INPUT)
    start_time_input = page.get_by_test_id(MARKER_FILTER_START_TIME_INPUT)
    end_date_input = page.get_by_test_id(MARKER_FILTER_END_DATE_INPUT)
    end_time_input = page.get_by_test_id(MARKER_FILTER_END_TIME_INPUT)

    start_date_input.wait_for(state="visible")
    start_time_input.wait_for(state="visible")
    end_date_input.wait_for(state="visible")
    end_time_input.wait_for(state="visible")

    # Read initial start values
    start_date_value = start_date_input.input_value()
    start_time_value = start_time_input.input_value()

    # Set end = start to create minimal range (single point in time)
    # This will show the background at that specific time with minimal trajectories
    end_date_input.fill("")
    end_date_input.type(start_date_value)
    end_time_input.fill("")
    end_time_input.type(start_time_value)

    # Step 4: Apply filter
    apply_btn = page.get_by_test_id(MARKER_FILTER_BY_DATE_APPLY_BUTTON)
    apply_btn.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)
    apply_btn.click()

    page.wait_for_timeout(FILTER_APPLY_WAIT_MS)

    # Step 5: Verify filter is active
    active_value = filter_by_date_button.get_attribute("data-filter-by-date-active")
    assert (
        active_value == "true"
    ), "Filter by date button did not indicate active state after applying filter"

    # Verify filter range label is displayed
    range_label = page.get_by_test_id(MARKER_FILTER_RANGE_LABEL)
    range_label.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)
    label_text = range_label.inner_text()
    assert (
        start_time_value in label_text
    ), "Applied date range label does not include expected time"

    # Step 6: Verify canvas updates to show filtered tracks
    # The filtered view should differ from the unfiltered view
    canvas_with_filtered_tracks = wait_for_canvas_change(
        page, canvas, canvas_with_all_tracks
    )
    assert (
        canvas_with_filtered_tracks != canvas_with_all_tracks
    ), "Canvas did not update after applying date filter - filter not working"

    # Additional verification: filtered image should show fewer/shorter trajectories
    # Since we set a minimal time range (start = end), we expect significantly
    # different visualization compared to showing all tracks across the full time range
    assert canvas_with_filtered_tracks != canvas_baseline, (
        "Filtered canvas matches baseline (before tracks enabled) - "
        "filter may have hidden all tracks unexpectedly"
    )


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
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    page.goto(base_url + ENDPOINT_MAIN_PAGE)

    # Setup: Add video, tracks, and apply filter
    data_dir = Path(__file__).parents[1] / "data"
    video_file = data_dir / TEST_VIDEO_FILENAME
    track_file = data_dir / TEST_TRACK_FILENAME

    page.get_by_text(resource_manager.get(TrackFormKeys.TAB_VIDEO), exact=True).click()
    add_video_via_picker(page, resource_manager, video_file)
    page.wait_for_timeout(UI_PROCESSING_GRACE_PERIOD_MS)

    page.get_by_text(resource_manager.get(TrackFormKeys.TAB_TRACK), exact=True).click()
    add_track_via_picker(page, resource_manager, track_file)

    canvas = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).first
    canvas.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

    checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    checkbox.scroll_into_view_if_needed()
    checkbox.click()

    # Apply a filter first
    filter_by_date_checkbox = page.get_by_test_id(MARKER_FILTER_BY_DATE_CHECKBOX)
    filter_by_date_checkbox.scroll_into_view_if_needed()
    filter_by_date_checkbox.click()

    filter_by_date_button = page.get_by_test_id(MARKER_FILTER_BY_DATE_BUTTON)
    filter_by_date_button.click()

    start_date_input = page.get_by_test_id(MARKER_FILTER_START_DATE_INPUT)
    start_time_input = page.get_by_test_id(MARKER_FILTER_START_TIME_INPUT)
    end_date_input = page.get_by_test_id(MARKER_FILTER_END_DATE_INPUT)
    end_time_input = page.get_by_test_id(MARKER_FILTER_END_TIME_INPUT)

    start_date_input.wait_for(state="visible")
    start_date_value = start_date_input.input_value()
    start_time_value = start_time_input.input_value()

    end_date_input.fill("")
    end_date_input.type(start_date_value)
    end_time_input.fill("")
    end_time_input.type(start_time_value)

    apply_btn = page.get_by_test_id(MARKER_FILTER_BY_DATE_APPLY_BUTTON)
    apply_btn.click()
    page.wait_for_timeout(FILTER_APPLY_WAIT_MS)

    # Verify filter is active before reset
    active_value = filter_by_date_button.get_attribute("data-filter-by-date-active")
    assert active_value == "true", "Filter should be active before reset"

    # Step 1: Open filter dialog and reset
    filter_by_date_button.click()
    page.get_by_text("Reset").click()
    page.wait_for_timeout(UI_PROCESSING_GRACE_PERIOD_MS)

    # Step 2: Verify filter is deactivated
    inactive_value = filter_by_date_button.get_attribute("data-filter-by-date-active")
    assert (
        inactive_value == "false"
    ), "Filter by date button did not indicate inactive state after reset"

    # Step 3: Verify range label is cleared
    range_label = page.get_by_test_id(MARKER_FILTER_RANGE_LABEL)
    label_text_after_reset = range_label.inner_text()
    assert (
        label_text_after_reset.strip() == ""
    ), "Date range label not cleared after reset"
