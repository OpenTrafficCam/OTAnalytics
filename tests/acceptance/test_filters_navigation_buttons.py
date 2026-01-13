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
    MARKER_FILTER_START_DATE_INPUT,
    MARKER_FILTER_START_TIME_INPUT,
    MARKER_NEXT_DATE_BUTTON,
    MARKER_NEXT_EVENT_BUTTON,
    MARKER_NEXT_FRAMES_BUTTON,
    MARKER_NEXT_SECONDS_BUTTON,
    MARKER_PREV_DATE_BUTTON,
    MARKER_PREV_EVENT_BUTTON,
    MARKER_PREV_FRAMES_BUTTON,
    MARKER_PREV_SECONDS_BUTTON,
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

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)

# Test data constants
TEST_VIDEO_FILENAME = "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
TEST_TRACK_FILENAME = "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.ottrk"


@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_filter_navigation_buttons(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """
    Acceptance (Playwright): Validate navigation buttons around the filter area.

    We intentionally reproduce the same setup as in the tracks test and end at the
    same point (after applying then resetting the date filter) before exercising
    the navigation buttons for Date, Seconds, Frames, and Event.
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

    # Switch to Tracks tab and add tracks
    page.get_by_text(resource_manager.get(TrackFormKeys.TAB_TRACK), exact=True).click()
    add_track_via_picker(page, resource_manager, track_file)

    # Get canvas reference
    canvas = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).first
    canvas.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

    # Enable tracks layer
    checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    checkbox.scroll_into_view_if_needed()
    checkbox.click()

    filter_by_date_checkbox = page.get_by_test_id(MARKER_FILTER_BY_DATE_CHECKBOX)
    filter_by_date_checkbox.click()
    filter_by_date_button = page.get_by_test_id(MARKER_FILTER_BY_DATE_BUTTON)
    filter_by_date_button.click()

    start_date_input = page.get_by_test_id(MARKER_FILTER_START_DATE_INPUT)
    start_time_input = page.get_by_test_id(MARKER_FILTER_START_TIME_INPUT)
    end_date_input = page.get_by_test_id(MARKER_FILTER_END_DATE_INPUT)
    end_time_input = page.get_by_test_id(MARKER_FILTER_END_TIME_INPUT)
    start_date_input.wait_for(state="visible")
    start_time_input.wait_for(state="visible")
    end_date_input.wait_for(state="visible")
    end_time_input.wait_for(state="visible")

    start_date_value = start_date_input.input_value()
    start_time_value = start_time_input.input_value()
    end_date_input.fill("")
    end_date_input.type(start_date_value)
    end_time_input.fill("")
    end_time_input.type(start_time_value)

    # Apply and then reset to reach same end state as previous test
    page.get_by_test_id(MARKER_FILTER_BY_DATE_APPLY_BUTTON).click()
    page.wait_for_timeout(200)
    filter_by_date_button.click()
    page.get_by_text("Reset").click()
    page.wait_for_timeout(150)

    # From here on, test the navigation buttons using canvas image change as oracle
    last_img = canvas.screenshot()

    def click_and_expect_change(test_id: str) -> bytes:
        """Click a navigation button and wait for canvas to change."""
        btn = page.get_by_test_id(test_id)
        btn.scroll_into_view_if_needed()
        # In case button is disabled in some states, try waiting briefly
        try:
            btn.wait_for(state="visible", timeout=2000)
        except Exception:
            pass
        btn.click()
        return wait_for_canvas_change(page, canvas, last_img)

    # Date range arrows
    after1 = click_and_expect_change(MARKER_NEXT_DATE_BUTTON)
    last_img = after1
    after2 = click_and_expect_change(MARKER_PREV_DATE_BUTTON)
    last_img = after2

    # Seconds arrows
    after3 = click_and_expect_change(MARKER_NEXT_SECONDS_BUTTON)
    last_img = after3
    after4 = click_and_expect_change(MARKER_PREV_SECONDS_BUTTON)
    last_img = after4

    # Frames arrows
    after5 = click_and_expect_change(MARKER_NEXT_FRAMES_BUTTON)
    last_img = after5
    after6 = click_and_expect_change(MARKER_PREV_FRAMES_BUTTON)
    last_img = after6

    # Event arrows
    after7 = click_and_expect_change(MARKER_NEXT_EVENT_BUTTON)
    last_img = after7
    after8 = click_and_expect_change(MARKER_PREV_EVENT_BUTTON)
    last_img = after8

    # Simple sanity: ensure we observed changes (non-empty progression)
    assert after1 != after2
    assert after3 != after4
    assert after5 != after6
    assert after7 != after8
