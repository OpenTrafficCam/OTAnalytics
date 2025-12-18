import time
from pathlib import Path

import pytest
from playwright.sync_api import Page  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import (
    AddTracksKeys,
    AddVideoKeys,
    ResourceManager,
    TrackFormKeys,
)
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
from tests.conftest import ACCEPTANCE_TEST_WAIT_TIMEOUT, NiceGUITestServer
from tests.utils.builders.otanalytics_builders import file_picker_directory

# Ensure pytest-playwright is available; otherwise skip this module
playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


def _open_part(page: Page, part: str) -> None:
    """Open a path segment inside the in-app file picker (ag-grid).

    Mirrors the approach used in other acceptance tests for navigating the picker.
    """
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            cell = page.locator(".ag-cell-value", has_text=part).first
            cell.wait_for(state="visible", timeout=1000)
            cell.dblclick()
            return
        except Exception as e:
            try:
                page.locator(".ag-cell-value").last.scroll_into_view_if_needed()
            except Exception:
                pass
            last_err = e
    if last_err:
        raise last_err
    raise AssertionError(f"Could not find table cell with text: {part}")


def _add_track_via_picker(page: Page, rm: ResourceManager, path: Path) -> None:
    """Click the Add button and navigate the picker to select the given track file.

    Be explicit about selecting the final file entry to ensure it is actually loaded.
    """
    # Open the picker
    page.get_by_text(rm.get(AddTracksKeys.BUTTON_ADD_TRACKS), exact=True).click()

    # Navigate directories, then explicitly select the file
    ui_path = path.relative_to(file_picker_directory())
    parts = list(ui_path.parts)
    if not parts:
        raise AssertionError("Resolved UI path has no parts")

    # Open all parent directories
    for part in parts[:-1]:
        _open_part(page, part)

    # Explicitly select the file in the grid (resilient lookup with retries)
    filename = parts[-1]
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    last_err: Exception | None = None
    file_cell = page.locator(".ag-cell-value", has_text=filename).first
    while time.time() < deadline:
        try:
            file_cell.wait_for(state="visible", timeout=750)
            break
        except Exception as e:
            last_err = e
            # Try to scroll within the grid in case the row is not in view yet
            try:
                page.locator(".ag-cell-value").last.scroll_into_view_if_needed()
            except Exception:
                pass
    if last_err:
        try:
            file_cell.wait_for(state="visible", timeout=250)
        except Exception:
            raise last_err

    # Click to select the row
    try:
        file_cell.click()
    except Exception:
        pass

    # Try to submit by pressing Enter (common in grids)
    try:
        file_cell.press("Enter")
    except Exception:
        pass

    # Fallback: double-click the file row to submit (picker supports this)
    try:
        file_cell.dblclick()
    except Exception:
        pass

    # Final fallback: if an OK button is visible, click it
    try:
        ok_btn = page.get_by_text("Ok", exact=True)
        # If it's visible, click to confirm selection
        ok_btn.wait_for(state="visible", timeout=1000)
        ok_btn.click()
    except Exception:
        # OK button might not be present or already closed
        pass


def _add_video_via_picker(page: Page, rm: ResourceManager, path: Path) -> None:
    """Open the in-app file picker and select a video file by navigating parts."""
    page.get_by_text(rm.get(AddVideoKeys.BUTTON_ADD_VIDEOS), exact=True).click()
    ui_path = path.relative_to(file_picker_directory())
    for part in ui_path.parts:
        _open_part(page, part)


@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_add_tracks_via_tracks_tab(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """Acceptance (Playwright): Open Tracks tab, click Add, select track file(s).

    Steps according to the issue:
    - Show "Tracks" tab by clicking on the Tracks/Track tab
    - Click "Add"
    - Select track files via the in-app file picker

    This test focuses on performing the UI interactions; assertions are minimal
    because the Tracks UI does not currently expose a table marker analogous to
    the Videos table. The primary goal is that the flow completes without error.
    """
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    page.goto(base_url + ENDPOINT_MAIN_PAGE)

    # First add a video (Videos tab) before adding tracks, mirroring other tests
    page.get_by_text(resource_manager.get(TrackFormKeys.TAB_TWO), exact=True).click()
    data_dir = Path(__file__).parents[1] / "data"
    video_file = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
    assert video_file.exists(), f"Test video file missing: {video_file}"
    _add_video_via_picker(page, resource_manager, video_file)
    page.wait_for_timeout(150)  # short grace period for backend/UI processing

    # Switch to Tracks tab (label is provided by resource manager; currently "Track")
    page.get_by_text(resource_manager.get(TrackFormKeys.TAB_ONE), exact=True).click()

    # Use a known test track file from the repository
    track_file = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.ottrk"
    assert track_file.exists(), f"Test track file missing: {track_file}"

    # Add the track via the picker
    _add_track_via_picker(page, resource_manager, track_file)

    # Allow a short grace period for the UI/backend to process the selection

    canvas = page.locator('[test-id="marker-interactive-image"]').first
    canvas.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)
    before = canvas.screenshot()

    # Enable the "All" tracks layer
    checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    checkbox.scroll_into_view_if_needed()
    checkbox.click()

    # Wait until the canvas content changes compared to the snapshot taken before
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    changed = False
    last_after: bytes | None = None
    while time.time() < deadline:
        try:
            # short grace period between polls to let the UI render
            page.wait_for_timeout(100)
            last_after = canvas.screenshot()
            if last_after != before:
                changed = True
                break
        except Exception:
            # If the element is momentarily updating, ignore and retry until deadline
            pass

    assert changed, "Canvas image did not change after enabling tracks layer"

    filter_by_date_checkbox = page.get_by_test_id(MARKER_FILTER_BY_DATE_CHECKBOX)
    filter_by_date_checkbox.scroll_into_view_if_needed()
    filter_by_date_checkbox.click()

    filter_by_date_button = page.get_by_test_id(MARKER_FILTER_BY_DATE_BUTTON)
    # Finally click the button (it should open the date range dialog)
    filter_by_date_button.click()

    start_date_input = page.get_by_test_id(MARKER_FILTER_START_DATE_INPUT)
    start_time_input = page.get_by_test_id(MARKER_FILTER_START_TIME_INPUT)
    end_date_input = page.get_by_test_id(MARKER_FILTER_END_DATE_INPUT)
    end_time_input = page.get_by_test_id(MARKER_FILTER_END_TIME_INPUT)

    # Ensure inputs are visible
    start_date_input.wait_for(state="visible")
    start_time_input.wait_for(state="visible")
    end_date_input.wait_for(state="visible")
    end_time_input.wait_for(state="visible")

    # Read start values as strings
    start_date_value = start_date_input.input_value()
    start_time_value = start_time_input.input_value()

    # Fill end date/time with the same values to create a minimal range
    end_date_input.fill("")
    end_date_input.type(start_date_value)
    end_time_input.fill("")
    end_time_input.type(start_time_value)

    # Record canvas before applying the filter to detect a visual change afterwards
    canvas_before_filter = canvas.screenshot()

    # Apply
    apply_btn = page.get_by_test_id(MARKER_FILTER_BY_DATE_APPLY_BUTTON)
    apply_btn.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)
    apply_btn.click()

    page.wait_for_timeout(200)
    active_value = filter_by_date_button.get_attribute("data-filter-by-date-active")
    assert (
        active_value == "true"
    ), "Filter by date button did not indicate active state after applying filter"

    range_label = page.get_by_test_id(MARKER_FILTER_RANGE_LABEL)
    range_label.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)
    label_text = range_label.inner_text()
    assert (
        start_time_value in label_text
    ), "Applied date range label does not include expected end time"

    deadline2 = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    changed_after_filter = False
    while time.time() < deadline2:
        page.wait_for_timeout(100)
        after_filter_img = canvas.screenshot()
        if after_filter_img != canvas_before_filter:
            changed_after_filter = True
            break
    assert changed_after_filter, "Canvas did not update after applying date filter"

    filter_by_date_button.click()
    page.get_by_text("Reset").click()
    page.wait_for_timeout(150)
    inactive_value = filter_by_date_button.get_attribute("data-filter-by-date-active")
    assert (
        inactive_value == "false"
    ), "Filter by date button did not indicate inactive state after reset"
    # Label may become empty when no date range is set
    label_text_after_reset = range_label.inner_text()
    assert (
        label_text_after_reset.strip() == ""
    ), "Date range label not cleared after reset"
