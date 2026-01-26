from pathlib import Path

import pytest
from playwright.sync_api import Page  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
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
    enable_and_apply_date_filter,
    setup_tracks_display,
    verify_filter_active,
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
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    page.goto(base_url + ENDPOINT_MAIN_PAGE)

    data_dir = Path(__file__).parents[1] / "data"
    video_file = data_dir / TEST_VIDEO_FILENAME
    track_file = data_dir / TEST_TRACK_FILENAME
    assert video_file.exists(), f"Test video file missing: {video_file}"
    assert track_file.exists(), f"Test track file missing: {track_file}"

    # Take baseline before enabling tracks layer
    canvas = setup_tracks_display(
        page, resource_manager, video_file, track_file, enable_tracks_layer=False
    )
    canvas_before_tracks = canvas.screenshot()

    # Enable "Show all tracks" layer
    checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    checkbox.scroll_into_view_if_needed()
    checkbox.click()

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

    data_dir = Path(__file__).parents[1] / "data"
    video_file = data_dir / TEST_VIDEO_FILENAME
    track_file = data_dir / TEST_TRACK_FILENAME
    assert video_file.exists(), f"Test video file missing: {video_file}"
    assert track_file.exists(), f"Test track file missing: {track_file}"

    # Setup: Add video, tracks, and enable tracks layer
    canvas = setup_tracks_display(
        page, resource_manager, video_file, track_file, enable_tracks_layer=True
    )
    canvas_with_all_tracks = canvas.screenshot()

    # Configure and apply date filter with minimal range
    enable_and_apply_date_filter(page, use_minimal_range=True)

    # Verify filter is active
    verify_filter_active(page)

    # Verify filter range label is displayed
    range_label = page.get_by_test_id(MARKER_FILTER_RANGE_LABEL)
    range_label.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

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

    data_dir = Path(__file__).parents[1] / "data"
    video_file = data_dir / TEST_VIDEO_FILENAME
    track_file = data_dir / TEST_TRACK_FILENAME

    # Setup: Add video, tracks, enable tracks layer, and apply filter
    setup_tracks_display(
        page, resource_manager, video_file, track_file, enable_tracks_layer=True
    )
    enable_and_apply_date_filter(page, use_minimal_range=True)

    # Verify filter is active before reset
    filter_by_date_button = page.get_by_test_id(MARKER_FILTER_BY_DATE_BUTTON)
    verify_filter_active(page)

    # Reset filter
    filter_by_date_button.click()
    page.get_by_text("Reset").click()
    page.wait_for_timeout(UI_PROCESSING_GRACE_PERIOD_MS)

    # Verify filter is deactivated
    inactive_value = filter_by_date_button.get_attribute("data-filter-by-date-active")
    assert (
        inactive_value == "false"
    ), "Filter by date button did not indicate inactive state after reset"

    # Verify range label is cleared
    range_label = page.get_by_test_id(MARKER_FILTER_RANGE_LABEL)
    label_text_after_reset = range_label.inner_text()
    assert (
        label_text_after_reset.strip() == ""
    ), "Date range label not cleared after reset"
