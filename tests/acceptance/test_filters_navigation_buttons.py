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
from tests.conftest import ACCEPTANCE_TEST_WAIT_TIMEOUT, NiceGUITestServer
from tests.utils.builders.otanalytics_builders import file_picker_directory

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


def _open_part(page: Page, part: str) -> None:
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


def _add_video_via_picker(page: Page, rm: ResourceManager, path: Path) -> None:
    page.get_by_text(rm.get(AddVideoKeys.BUTTON_ADD_VIDEOS), exact=True).click()
    ui_path = path.relative_to(file_picker_directory())
    for part in ui_path.parts:
        _open_part(page, part)


def _add_track_via_picker(page: Page, rm: ResourceManager, path: Path) -> None:
    page.get_by_text(rm.get(AddTracksKeys.BUTTON_ADD_TRACKS), exact=True).click()
    ui_path = path.relative_to(file_picker_directory())
    parts = list(ui_path.parts)
    for part in parts[:-1]:
        _open_part(page, part)
    filename = parts[-1]
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    file_cell = page.locator(".ag-cell-value", has_text=filename).first
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            file_cell.wait_for(state="visible", timeout=750)
            break
        except Exception as e:
            last_err = e
            try:
                page.locator(".ag-cell-value").last.scroll_into_view_if_needed()
            except Exception:
                pass
    if last_err:
        try:
            file_cell.wait_for(state="visible", timeout=250)
        except Exception:
            raise last_err
    try:
        file_cell.click()
    except Exception:
        pass
    try:
        file_cell.press("Enter")
    except Exception:
        pass
    try:
        file_cell.dblclick()
    except Exception:
        pass
    try:
        ok_btn = page.get_by_text("Ok", exact=True)
        ok_btn.wait_for(state="visible", timeout=1000)
        ok_btn.click()
    except Exception:
        pass


def _wait_canvas_change(page: Page, baseline: bytes) -> bytes:
    canvas = page.locator('[test-id="marker-interactive-image"]').first
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    while time.time() < deadline:
        page.wait_for_timeout(100)
        img = canvas.screenshot()
        if img != baseline:
            return img
    # If we reach here, the canvas did not change within the timeout; fail the test
    pytest.fail("Timed out waiting for canvas image to change", pytrace=False)


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

    # Add a video first
    data_dir = Path(__file__).parents[1] / "data"
    video_file = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
    assert video_file.exists(), f"Test video file missing: {video_file}"
    page.get_by_text(resource_manager.get(TrackFormKeys.TAB_TWO), exact=True).click()
    _add_video_via_picker(page, resource_manager, video_file)

    # Switch to Tracks tab and add tracks
    page.get_by_text(resource_manager.get(TrackFormKeys.TAB_ONE), exact=True).click()
    track_file = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.ottrk"
    assert track_file.exists(), f"Test track file missing: {track_file}"
    _add_track_via_picker(page, resource_manager, track_file)

    # Canvas reference
    canvas = page.locator('[test-id="marker-interactive-image"]').first
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
        btn = page.get_by_test_id(test_id)
        btn.scroll_into_view_if_needed()
        # In case button is disabled in some states, try waiting briefly
        try:
            btn.wait_for(state="visible", timeout=2000)
        except Exception:
            pass
        btn.click()
        return _wait_canvas_change(page, last_img)

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
