import json
import logging
import time
from pathlib import Path
from typing import Any, Iterable

import pytest
from PIL import Image, ImageChops  # type: ignore
from playwright.sync_api import Error, Page, TimeoutError

from OTAnalytics.adapter_ui.dummy_viewmodel import SUPPORTED_VIDEO_FILE_TYPES
from OTAnalytics.application.resources.resource_manager import (
    AddTracksKeys,
    AddVideoKeys,
    FlowAndSectionKeys,
    FlowKeys,
    ResourceManager,
    SectionKeys,
    TrackFormKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.edit_flow_dialog import (
    MARKER_END_SECTION,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.edit_flow_dialog import (
    MARKER_NAME as MARKER_FLOW_NAME,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.edit_flow_dialog import (
    MARKER_START_SECTION,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.edit_section_dialog import (
    MARKER_NAME as MARKER_SECTION_NAME,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_chooser_dialog import (
    MARKER_DIRECTORY,
    MARKER_FILENAME,
)
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import (
    MARKER_APPLY as MARKER_DIALOG_APPLY,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.container import (
    MARKER_VIDEO_TAB,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.visualization_offset_slider_form import (  # noqa
    MARKER_UPDATE_OFFSET,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_video_form.container import (
    MARKER_BUTTON_ADD as MARKER_VIDEO_ADD,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_video_form.container import (
    MARKER_VIDEO_TABLE,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (
    MARKER_INTERACTIVE_IMAGE,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.configuration_bar.project_form import (
    MARKER_PROJECT_NAME,
    MARKER_PROJECT_OPEN,
    MARKER_PROJECT_SAVE_AS,
    MARKER_START_DATE,
    MARKER_START_TIME,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.flow_form import (
    MARKER_BUTTON_ADD as MARKER_FLOW_ADD,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.flow_form import (
    MARKER_FLOW_TABLE,
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
    MARKER_UPDATE_FLOW_HIGHLIGHTING,
    MARKER_VISUALIZATION_LAYERS_ALL,
)
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID
from tests.acceptance.conftest import (
    ACCEPTANCE_TEST_TRACK_FILES,
    ACCEPTANCE_TEST_VIDEO_FILE,
    ACCEPTANCE_TEST_WAIT_TIMEOUT,
    IMPORT_VERIFY_MAX_POLLS,
    PLAYWRIGHT_POLL_INTERVAL_MS,
    PLAYWRIGHT_POLL_INTERVAL_SECONDS,
    PLAYWRIGHT_POLL_INTERVAL_SLOW_MS,
    PLAYWRIGHT_SHORT_WAIT_MS,
    PLAYWRIGHT_VISIBLE_TIMEOUT_MS,
)
from tests.utils.builders.otanalytics_builders import file_picker_directory

logger = logging.getLogger(__name__)


def set_input_value_via_marker(page: Page, marker: str, value: str) -> None:
    set_input_value(page, f'[{TEST_ID}="{marker}"]', value)


def set_input_value(page: Page, selector: str, value: str) -> None:
    """Robustly set a value on an input and ensure NiceGUI backend receives it.

    Strategy:
    - Click, fill, press Enter to commit, and blur to trigger NiceGUI's value change.
    - Additionally set value via evaluate() and dispatch input/change as a fallback.
    """
    loc = page.locator(selector).first
    loc.wait_for(state="visible")
    try:
        loc.click()
    except (TimeoutError, Error) as e:
        logger.warning(
            "set_input_value: click() failed for selector %s: %s", selector, e
        )
    try:
        loc.fill("")
        loc.fill(value)
        try:
            loc.press("Enter")
        except (TimeoutError, Error) as e:
            logger.warning(
                "set_input_value: press('Enter') failed for selector %s: %s",
                selector,
                e,
            )
    except (TimeoutError, Error) as e:
        # ignore fill issues, will fallback to JS below if verification fails
        logger.warning(
            "set_input_value: fill() failed for selector %s: %s", selector, e
        )

    page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_MS)

    # Verify the value was actually set (short retry to avoid flakiness)
    def verify(expected: str) -> tuple[bool, str | None]:
        deadline = time.time() + PLAYWRIGHT_POLL_INTERVAL_SECONDS * 3
        last_local: str | None = None
        while time.time() < deadline:
            try:
                last_local = loc.input_value()
            except (TimeoutError, Error) as err:
                logger.warning(
                    "set_input_value: input_value() failed for selector %s: %s",
                    selector,
                    err,
                )
                last_local = None
            if last_local == expected:
                return True, last_local
            page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_MS)
        return False, last_local

    ok, last = verify(value)
    if not ok:
        # Fallback: ensure events are dispatched and element is blurred, then re-verify
        logger.info("set_input_value: engaging JS fallback for selector %s", selector)
        loc.evaluate(
            "(el, v) => {\n"
            "  el.value = v;\n"
            "  el.dispatchEvent(new Event('input', { bubbles: true }));\n"
            "  el.dispatchEvent(new Event('change', { bubbles: true }));\n"
            "  if (el.blur) el.blur();\n"
            "}",
            value,
        )
        page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_MS)
        ok, last = verify(value)

    assert (
        ok and last == value
    ), f"Failed to set input value: expected '{value}', got '{last}' for selector {selector}"  # noqa


def navigate_and_prepare(
    page: Page,
    external_app: object,
    resource_manager: ResourceManager,
    *,
    name: str = "Test Project - Flow E2E",
    date_value: str = "2023-05-24",
    time_value: str = "06:00:00",
) -> None:
    """Open main page and fill basic project information.

    This consolidates the repeated setup used by acceptance tests.
    """
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    page.goto(base_url + ENDPOINT_MAIN_PAGE)
    fill_project_information(
        page,
        resource_manager,
        name=name,
        date_value=date_value,
        time_value=time_value,
    )


def search_for_marker_element(page: Page, marker: str) -> Any:
    """Return a Playwright locator for elements marked with our test attribute.

    Usage:
        search_for_marker_element(page, MARKER_FILENAME).first.fill("test_name")
    """
    return page.locator(f'[{TEST_ID}="{marker}"]')


def fill_project_information(
    page: Page,
    resource_manager: ResourceManager,
    name: str = "Test Project",
    date_value: str = "2023-05-24",
    time_value: str = "06:00:00",
) -> None:
    """Fill the mandatory project information fields on the main page."""
    set_input_value_via_marker(page, MARKER_PROJECT_NAME, name)
    set_input_value_via_marker(page, MARKER_START_DATE, date_value)
    set_input_value_via_marker(page, MARKER_START_TIME, time_value)


def save_project_otconfig(
    page: Page, resource_manager: ResourceManager, target_path: Path
) -> None:
    """Open the Save As dialog and save the project configuration to target_path.

    This encapsulates the marker-driven dialog interaction to reduce duplication
    in tests. Filename field expects the name without extension.
    """
    # Open Save As dialog
    search_for_marker_element(page, MARKER_PROJECT_SAVE_AS).first.click()
    # Wait for dialog to be visible
    search_for_marker_element(page, MARKER_DIALOG_APPLY).first.wait_for(state="visible")
    # Fill directory and filename (stem without suffix)
    search_for_marker_element(page, MARKER_DIRECTORY).first.fill(
        str(target_path.parent)
    )
    search_for_marker_element(page, MARKER_FILENAME).first.fill(target_path.stem)
    # Confirm save
    search_for_marker_element(page, MARKER_DIALOG_APPLY).first.click()


# ----------------------
# Shared Playwright helpers
# ----------------------


def table_filenames(page: Page) -> list[str]:
    """Return list of video file names currently shown in the add-video table."""
    cells = search_for_marker_element(page, MARKER_VIDEO_TABLE).locator(
        "table tbody tr td"
    )
    texts = [text.strip() for text in cells.all_inner_texts()]
    return [
        t
        for t in texts
        if any(t.lower().endswith(e) for e in SUPPORTED_VIDEO_FILE_TYPES)
    ]


def wait_for_names_present(page: Page, names: Iterable[str]) -> None:
    """Wait until all provided names are present in the video table."""
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    names = list(names)
    while time.time() < deadline:
        listed = table_filenames(page)
        if all(n in listed for n in names):
            return
        time.sleep(PLAYWRIGHT_POLL_INTERVAL_SECONDS)
    raise AssertionError(
        f"Timed out waiting for names to appear: {names}; "
        f"currently: {table_filenames(page)}"
    )


def wait_for_names_gone(page: Page, names: Iterable[str]) -> None:
    """Wait until all provided names are gone from the video table."""
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    names = list(names)
    while time.time() < deadline:
        listed = table_filenames(page)
        if all(n not in listed for n in names):
            return
        time.sleep(PLAYWRIGHT_POLL_INTERVAL_SECONDS)
    raise AssertionError(
        f"Timed out waiting for names to disappear: {names}; "
        f"currently: {table_filenames(page)}"
    )


def click_table_cell_with_text(page: Page, text: str) -> None:
    """Click the first cell in the video table that contains the given text."""
    cell = (
        search_for_marker_element(page, MARKER_VIDEO_TABLE)
        .locator("table tbody tr td", has_text=text)
        .first
    )
    cell.wait_for(state="visible")
    cell.click()


def reset_videos_tab(page: Page, rm: ResourceManager) -> None:
    """Remove all videos currently listed in the Videos tab (best effort)."""
    for _ in range(50):
        names = table_filenames(page)
        if not names:
            break
        name = names[0]
        try:
            click_table_cell_with_text(page, name)
            page.get_by_text(
                rm.get(AddVideoKeys.BUTTON_REMOVE_VIDEOS), exact=True
            ).click()
            # wait until it's gone
            wait_for_names_gone(page, [name])
        except Exception:
            # Best-effort cleanup only
            break


def go_to_sections_with_one_video(page: Page, rm: ResourceManager) -> None:
    """Prepare UI with a single video selected and switch to the Sections tab.

    Steps:
    - Open the Videos tab (by stable marker if available; fallback to tab text)
    - Reset any existing videos
    - Add one known test video via the in-app picker
    - Select the video row to render a frame
    - Switch to the Sections tab
    """
    # Prefer stable marker to open Videos tab; fallback to text if needed
    try:
        search_for_marker_element(page, MARKER_VIDEO_TAB).first.click()
    except Exception:
        page.get_by_text(rm.get(TrackFormKeys.TAB_VIDEO), exact=True).click()

    # Ensure a clean slate
    reset_videos_tab(page, rm)

    # Add a known test video
    data_dir = Path(__file__).parents[1] / "data"
    v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
    assert v1.exists(), f"Test video missing: {v1}"
    add_video_via_picker(page, rm, v1)

    # Wait until it appears and select it
    wait_for_names_present(page, [v1.name])
    click_table_cell_with_text(page, v1.name)

    # Switch to Sections tab
    page.get_by_text(rm.get(FlowAndSectionKeys.TAB_SECTION), exact=True).click()


def open_part(page: Page, part: str) -> None:
    """Double-click a cell in the file picker grid matching the given text."""
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            # Look for the row in the ag-grid that contains the text
            # The file picker shows folders as "📁 <strong>foldername</strong>"
            row = (
                page.locator(".ag-center-cols-container .ag-row")
                .filter(has_text=part)
                .first
            )
            row.wait_for(state="visible", timeout=2000)
            row.dblclick()
            # Wait for directory to load after double-click
            page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_SLOW_MS)
            return
        except Exception as e:
            # Try to scroll if possible
            try:
                last_row = page.locator(".ag-center-cols-container .ag-row").last
                last_row.scroll_into_view_if_needed()
            except Exception:
                pass
            last_err = e
            page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_MS)
    if last_err:
        # Try to capture screenshot and grid content for debugging
        try:
            screenshot_path = f"/tmp/file_picker_failure_{part}.png"
            page.screenshot(path=screenshot_path)
            logger.error(f"Screenshot saved to: {screenshot_path}")
        except Exception:
            pass

        try:
            # Log what's actually in the grid
            all_cells = page.locator(".ag-cell-value").all_inner_texts()
            logger.error(
                f"Grid contains {len(all_cells)} cells. First 20: {all_cells[:20]}"
            )
        except Exception:
            pass

        raise last_err
    raise AssertionError(f"Could not find table cell with text: {part}")


def add_video_via_picker(page: Page, rm: ResourceManager, path: Path) -> None:
    """Open the in-app file picker and navigate to select the given video path."""
    # Prefer stable marker-based lookup; fall back to label if marker is unavailable
    try:
        add_button = search_for_marker_element(page, MARKER_VIDEO_ADD).first
        add_button.wait_for(state="visible", timeout=2000)
    except (TimeoutError, Error):
        # Fallback to searching by button text
        button_text = rm.get(AddVideoKeys.BUTTON_ADD_VIDEOS)
        add_button = page.get_by_text(button_text, exact=True)
        add_button.wait_for(
            state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000
        )
    add_button.click()

    # Wait for file picker dialog to open
    page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_SLOW_MS)

    ui_path = path.relative_to(file_picker_directory())
    for part in ui_path.parts:
        open_part(page, part)


def open_project_otconfig(page: Page, rm: ResourceManager, path: Path) -> None:
    """Open a project .otconfig file via the NiceGUI file chooser.

    This encapsulates the repeated steps used across acceptance tests to open
    a project configuration:
    - Click the project 'Open' action (by marker or label fallback)
    - Wait for the file chooser dialog
    - Fill directory and filename via test-id markers
    - Apply the dialog
    """

    search_for_marker_element(page, MARKER_PROJECT_OPEN).first.click()
    # Interact with the FileChooserDialog to choose the file using markers
    search_for_marker_element(page, MARKER_DIALOG_APPLY).first.wait_for(state="visible")
    search_for_marker_element(page, MARKER_DIRECTORY).first.fill(str(path.parent))
    search_for_marker_element(page, MARKER_FILENAME).first.fill(path.name)
    search_for_marker_element(page, MARKER_DIALOG_APPLY).first.click()


# ----------------------
# Save / Export helpers
# ----------------------


def save_project_as(page: Page, rm: ResourceManager, path: Path) -> None:
    """Open the Save Project dialog and save to the given ``path``.

    - Click the 'Save project as' action (by marker with label fallback).
    - Fill the directory and filename in the NiceGUI file chooser via markers.
    - Apply the dialog.
    """
    search_for_marker_element(page, MARKER_PROJECT_SAVE_AS).first.click()

    # Interact with the FileChooserDialog
    search_for_marker_element(page, MARKER_DIALOG_APPLY).first.wait_for(state="visible")
    # Normalize filename: prefer basename without .otconfig extension if present
    filename = path.name[:-9] if path.name.endswith(".otconfig") else path.name
    search_for_marker_element(page, MARKER_DIRECTORY).first.fill(str(path.parent))
    search_for_marker_element(page, MARKER_FILENAME).first.fill(filename)
    search_for_marker_element(page, MARKER_DIALOG_APPLY).first.click()


# ----------------------
# File comparison helpers
# ----------------------


def compare_json_files(saved_path: Path, reference_path: Path) -> None:
    """Load two JSON files and assert their content is identical.

    Parameters
    - saved_path: the path to the produced/output JSON file
    - reference_path: the path to the expected/reference JSON file

    Raises
    - AssertionError if files do not exist or JSON payloads differ
    """
    assert saved_path.exists(), f"Expected saved configuration at {saved_path}"
    assert reference_path.exists(), f"Reference configuration missing: {reference_path}"
    with (
        saved_path.open("r", encoding="utf-8") as fa,
        reference_path.open("r", encoding="utf-8") as fb,
    ):
        ja = json.load(fa)  # type: ignore[name-defined]
        jb = json.load(fb)  # type: ignore[name-defined]
    assert ja == jb, (
        "Saved configuration does not match reference file\n"
        f"Saved: {saved_path}\nReference: {reference_path}"
    )


# ----------------------
# Project Information helpers
# ----------------------


def read_project_info_values(page: Page) -> tuple[str, str, str]:
    """Read current values from the Project form inputs using test-id markers."""
    return (
        search_for_marker_element(page, MARKER_PROJECT_NAME).input_value(),
        search_for_marker_element(page, MARKER_START_DATE).input_value(),
        search_for_marker_element(page, MARKER_START_TIME).input_value(),
    )


def import_project_and_assert_values(
    page: Page,
    rm: ResourceManager,
    path: Path,
    expected: tuple[str, str, str],
) -> None:
    """Import a project .otconfig and wait until Project form shows expected values.

    - Uses the NiceGUI file chooser via `open_project_otconfig`.
    - Polls the UI for a short time until the values match `expected`.
    - Asserts final values equal `expected`.
    """
    open_project_otconfig(page, rm, path)
    # Give backend a moment to propagate values
    page.wait_for_timeout(PLAYWRIGHT_SHORT_WAIT_MS)
    name_v, date_v, time_v = read_project_info_values(page)
    for _ in range(IMPORT_VERIFY_MAX_POLLS):
        if (name_v, date_v, time_v) == expected:
            break
        page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_MS)
        name_v, date_v, time_v = read_project_info_values(page)
    assert (name_v, date_v, time_v) == expected


# ----------------------
# Sections helpers
# ----------------------


def create_section(
    page: Page,
    rm: ResourceManager,
    section_name: str = "Name",
    positions: list[tuple[int, int]] | None = None,
) -> None:
    """Create a line section on the canvas via dialog and assert it's visible.

    Steps:
    - Ensure interactive image is visible and scrolled into view
    - Click the 'Add line' button if present
    - Click on provided canvas positions to define the line
    - Press Enter to open the section dialog, fill name and apply
    - Poll until the section name appears in page content
    """
    if positions is None:
        positions = [(20, 20), (140, 60), (260, 120)]

    canvas_locator = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE)
    canvas_locator.wait_for(state="visible")
    img = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).locator("img").first
    target = img if img.count() else canvas_locator
    try:
        target.scroll_into_view_if_needed()
    except Exception:
        pass

    # Try to click the add line button by label
    try:
        page.get_by_text(rm.get(SectionKeys.BUTTON_ADD_LINE), exact=True).click()
    except Exception:
        # ignore if already active or button not present
        pass

    # Click the positions on the canvas/image
    for x, y in positions:
        try:
            target.click(position={"x": x, "y": y})
        except Exception:
            canvas_locator.click(position={"x": x, "y": y})

    # Confirm to open dialog
    page.keyboard.press("Enter")

    # Fill name in dialog (input may be wrapped or be the element itself)
    ni = search_for_marker_element(page, MARKER_SECTION_NAME).locator("input").first
    if not ni.count():
        ni = search_for_marker_element(page, MARKER_SECTION_NAME).first
    ni.wait_for(state="visible")
    try:
        ni.fill(section_name)
    except Exception:
        # Fallback via set_input_value if needed
        sel = ni.selector() if hasattr(ni, "selector") else None
        if sel:
            set_input_value(page, sel, section_name)
        else:
            ni.fill(section_name)
    ab = search_for_marker_element(page, MARKER_DIALOG_APPLY).first
    ab.wait_for(state="visible")
    ab.click()

    # Wait until section name is present somewhere in the page
    deadline_local = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    while time.time() < deadline_local:
        try:
            if section_name in page.content():
                return
        except Exception:
            pass
        time.sleep(PLAYWRIGHT_POLL_INTERVAL_SLOW_MS / 1000)
    raise AssertionError(f"Section name not found after apply: {section_name}")


def create_flow(
    page: Page,
    rm: ResourceManager,
    flow_name: str,
    start_section_index: int = 0,
    end_section_index: int = 1,
) -> None:
    """Helper to create a flow through the dialog.

    Assumes we are already on the Flows tab.
    """
    try:
        page.get_by_text(rm.get(FlowKeys.BUTTON_ADD), exact=True).click()
    except Exception:
        search_for_marker_element(page, MARKER_FLOW_ADD).first.click()

    search_for_marker_element(page, MARKER_FLOW_NAME).first.wait_for(state="visible")
    search_for_marker_element(page, MARKER_FLOW_NAME).first.fill(flow_name)

    # Select start section
    search_for_marker_element(page, MARKER_START_SECTION).first.click()
    for _ in range(start_section_index + 1):
        page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")

    # Select end section
    search_for_marker_element(page, MARKER_END_SECTION).first.click()
    for _ in range(end_section_index + 1):
        page.keyboard.press("ArrowDown")
    page.keyboard.press("Enter")

    search_for_marker_element(page, MARKER_DIALOG_APPLY).first.click()


def wait_for_flow_present(page: Page, flow_name: str) -> None:
    """Wait until the flow name appears in the flow table."""
    table = search_for_marker_element(page, MARKER_FLOW_TABLE).first
    table.wait_for(state="visible")
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    while time.time() < deadline:
        try:
            if flow_name in table.inner_text():
                return
        except Exception:
            pass
        time.sleep(PLAYWRIGHT_POLL_INTERVAL_SECONDS)
    raise AssertionError(f"Flow '{flow_name}' did not appear in table")


# ----------------------
# Canvas helpers
# ----------------------


def toggle_and_screenshot(
    page: Page,
    canvas: Any,
    checkbox_text: str,
    screenshot_folder: Path,
    filename_base: str,
    nth: int = 0,
    timeout_ms: int = PLAYWRIGHT_VISIBLE_TIMEOUT_MS,
) -> None:
    """Toggle a checkbox on, take screenshot, then toggle off.

    Args:
        page: Playwright page object
        canvas: Canvas locator for taking screenshots
        checkbox_text: Text of the checkbox to find
        screenshot_folder: Folder where screenshots will be saved
        filename_base: Base name for screenshot files
        nth: Which occurrence to use if multiple checkboxes have same text
        timeout_ms: Timeout in milliseconds to wait after toggling
    """
    checkbox = page.get_by_text(checkbox_text, exact=True).nth(nth)
    checkbox.scroll_into_view_if_needed()

    # Toggle on and screenshot
    if not checkbox.is_checked():
        checkbox.click()
    page.wait_for_timeout(timeout_ms)
    canvas.screenshot(path=screenshot_folder / f"{filename_base}.png")

    # Toggle off (no screenshot)
    checkbox.click()
    page.wait_for_timeout(timeout_ms)


def wait_for_canvas_change(
    page: Page, canvas_locator: Any, baseline: bytes, timeout: float | None = None
) -> bytes:
    """Wait until canvas image changes from baseline.

    Args:
        page: Playwright page object
        canvas_locator: Locator for the canvas element
        baseline: Baseline screenshot bytes to compare against
        timeout: Optional timeout in seconds (defaults to ACCEPTANCE_TEST_WAIT_TIMEOUT)

    Returns:
        The new screenshot bytes after change is detected

    Raises:
        AssertionError: If canvas does not change within timeout
    """
    if timeout is None:
        timeout = ACCEPTANCE_TEST_WAIT_TIMEOUT
    deadline = time.time() + timeout
    while time.time() < deadline:
        page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_MS)
        current = canvas_locator.screenshot()
        if current != baseline:
            return current
    raise AssertionError("Canvas did not change within timeout")


def compare_screenshots(actual: bytes, expected: bytes) -> bool:
    """Compare two screenshot byte arrays for equality.

    Args:
        actual: Actual screenshot bytes to compare
        expected: Expected screenshot bytes to compare against

    Returns:
        True if screenshots match, False otherwise
    """
    return actual == expected


# ----------------------
# Track helpers
# ----------------------


def setup_tracks_display(
    page: Page,
    rm: ResourceManager,
    video_file: Path,
    track_file: Path | list[Path],
    enable_tracks_layer: bool = True,
) -> Any:
    """Setup for tracks display: add video, tracks, optionally enable layer.

    Args:
        page: Playwright page object
        rm: ResourceManager for localized strings
        video_file: Path to video file
        track_file: Path to track file or list of track files
        enable_tracks_layer: Whether to enable "Show all tracks" layer (default: True)

    Returns:
        Canvas locator that can be used for screenshots/verification
    """
    # Wait for page to be fully loaded by checking for "Project" text
    page.get_by_text("Project").first.wait_for(
        state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000
    )

    # Add video
    video_tab = page.get_by_text(rm.get(TrackFormKeys.TAB_VIDEO), exact=True)
    video_tab.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)
    video_tab.click()
    page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_MS)
    add_video_via_picker(page, rm, video_file)
    page.wait_for_timeout(150)

    # Add tracks
    page.get_by_text(rm.get(TrackFormKeys.TAB_TRACK), exact=True).click()
    track_files = track_file if isinstance(track_file, list) else [track_file]
    for tf in track_files:
        add_track_via_picker(page, rm, tf)

    # Get canvas reference
    canvas = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).first
    canvas.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

    # Enable tracks layer if requested
    if enable_tracks_layer:
        checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
        checkbox.scroll_into_view_if_needed()
        checkbox.click()
        page.wait_for_timeout(200)

    return canvas


def enable_and_apply_date_filter(
    page: Page,
    *,
    use_minimal_range: bool = True,
    custom_start_date: str | None = None,
    custom_start_time: str | None = None,
    custom_end_date: str | None = None,
    custom_end_time: str | None = None,
) -> None:
    """Enable date filter checkbox, open dialog, configure, and apply.

    Args:
        page: Playwright page object
        use_minimal_range: If True, sets end = start for minimal range (default: True)
        custom_start_date: Optional custom start date (format: YYYY-MM-DD)
        custom_start_time: Optional custom start time (format: HH:MM:SS)
        custom_end_date: Optional custom end date (format: YYYY-MM-DD)
        custom_end_time: Optional custom end time (format: HH:MM:SS)
    """
    # Enable filter checkbox
    filter_checkbox = page.get_by_test_id(MARKER_FILTER_BY_DATE_CHECKBOX)
    filter_checkbox.scroll_into_view_if_needed()
    filter_checkbox.wait_for(
        state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000
    )

    # Check if already checked
    if not filter_checkbox.is_checked():
        filter_checkbox.click()
        page.wait_for_timeout(500)  # Wait for button to become enabled

    # Open filter dialog
    filter_button = page.get_by_test_id(MARKER_FILTER_BY_DATE_BUTTON)
    # Wait for button to be enabled after checkbox is checked
    filter_button.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

    # Wait for button to be enabled (not disabled)
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    while time.time() < deadline:
        disabled_attr = filter_button.get_attribute("disabled")
        if disabled_attr is None:
            break
        page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_MS)

    # Force click even if appears disabled (might be a visual state issue)
    filter_button.click(force=True)

    # Get input elements
    start_date_input = page.get_by_test_id(MARKER_FILTER_START_DATE_INPUT)
    start_time_input = page.get_by_test_id(MARKER_FILTER_START_TIME_INPUT)
    end_date_input = page.get_by_test_id(MARKER_FILTER_END_DATE_INPUT)
    end_time_input = page.get_by_test_id(MARKER_FILTER_END_TIME_INPUT)

    start_date_input.wait_for(state="visible")
    start_time_input.wait_for(state="visible")
    end_date_input.wait_for(state="visible")
    end_time_input.wait_for(state="visible")

    # Configure filter range
    if custom_start_date:
        start_date_input.fill("")
        start_date_input.type(custom_start_date)
    if custom_start_time:
        start_time_input.fill("")
        start_time_input.type(custom_start_time)

    if use_minimal_range and not (custom_end_date or custom_end_time):
        # Set end = start for minimal range
        start_date_value = start_date_input.input_value()
        start_time_value = start_time_input.input_value()
        end_date_input.fill("")
        end_date_input.type(start_date_value)
        end_time_input.fill("")
        end_time_input.type(start_time_value)
    else:
        if custom_end_date:
            end_date_input.fill("")
            end_date_input.type(custom_end_date)
        if custom_end_time:
            end_time_input.fill("")
            end_time_input.type(custom_end_time)

    # Apply filter
    apply_btn = page.get_by_test_id(MARKER_FILTER_BY_DATE_APPLY_BUTTON)
    apply_btn.click()
    page.wait_for_timeout(200)


def verify_filter_active(page: Page) -> None:
    """Verify that the date filter is active by checking button attribute."""

    # Wait a bit for filter to be applied
    page.wait_for_timeout(500)

    filter_button = page.get_by_test_id(MARKER_FILTER_BY_DATE_BUTTON)
    filter_button.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

    # Wait for the attribute to be set
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    while time.time() < deadline:
        active_value = filter_button.get_attribute("data-filter-by-date-active")
        if active_value == "true":
            return
        page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_MS)

    # Final check
    active_value = filter_button.get_attribute("data-filter-by-date-active")
    assert active_value == "true", f"Filter is not active (value: {active_value})"


def add_track_via_picker(page: Page, rm: ResourceManager, path: Path) -> None:
    """Add a track file via the in-app file picker.

    Uses the same approach as add_video_via_picker for consistency.
    """
    page.get_by_text(rm.get(AddTracksKeys.BUTTON_ADD_TRACKS), exact=True).click()

    # Wait for file picker dialog to open
    page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_SLOW_MS)

    # Navigate and select file (same as video picker)
    ui_path = path.relative_to(file_picker_directory())
    for part in ui_path.parts:
        open_part(page, part)


def setup_with_preconfigured_otconfig(
    page: Page,
    rm: ResourceManager,
    otconfig_path: Path,
) -> None:
    """Load a pre-configured .otconfig file
    that already has video, tracks, and sections.

    This skips the individual steps of loading video,
    adding tracks, and creating sections
    by loading a configuration file that already contains all of that setup.

    Args:
        page: Playwright page object
        rm: ResourceManager for localized strings
        otconfig_path: Path to the pre-configured .otconfig file
    """
    # Wait for page to be ready
    page.get_by_text("Project").first.wait_for(
        state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000
    )

    # Load the pre-configured project file
    open_project_otconfig(page, rm, otconfig_path)

    # Wait for the project to load
    page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_SLOW_MS)

    # Verify canvas is visible (indicating project loaded successfully)
    canvas = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).first
    canvas.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)


# ----------------------
# Test helper functions for tracks display tests
# ----------------------


def navigate_to_main_page_with_url(page: Page, base_url: str) -> None:
    """Navigate to the main page of the application."""
    page.goto(base_url + ENDPOINT_MAIN_PAGE)


def load_main_page(page: Page, external_app: Any) -> None:
    """Load the main page from external_app.

    Args:
        page: Playwright page object
        external_app: NiceGUITestServer instance with base_url attribute
    """
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
    page.goto(base_url + ENDPOINT_MAIN_PAGE)


def get_test_files_from_data_dir(data_dir: Path) -> tuple[Path, list[Path]]:
    """Get paths to test video and track files.

    Args:
        data_dir: Path to the data directory containing test files

    Returns:
        Tuple of (video_file, list of track_files)

    Raises:
        AssertionError: If test files are missing
    """

    video_file = data_dir / ACCEPTANCE_TEST_VIDEO_FILE
    track_files = [data_dir / filename for filename in ACCEPTANCE_TEST_TRACK_FILES]
    assert video_file.exists(), f"Test video file missing: {video_file}"
    for track_file in track_files:
        assert track_file.exists(), f"Test track file missing: {track_file}"
    return video_file, track_files


def enable_all_tracks_layer(page: Page) -> None:
    """Enable the 'Show all tracks' layer."""
    checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    checkbox.scroll_into_view_if_needed()
    checkbox.click()


def update_flow_highlighting(
    page: Page, timeout_ms: int = PLAYWRIGHT_VISIBLE_TIMEOUT_MS
) -> None:
    """Click the 'Update flow highlighting' button and wait for processing.

    Args:
        page: Playwright page object
        timeout_ms: Timeout in milliseconds to wait after
        clicking (default: PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
    """
    button = page.get_by_test_id(MARKER_UPDATE_FLOW_HIGHLIGHTING)
    button.scroll_into_view_if_needed()
    button.click()
    page.wait_for_timeout(timeout_ms)


def click_update_offset_button(
    page: Page,
    canvas: Any,
    screenshot_folder: Path,
    timeout_ms: int = PLAYWRIGHT_VISIBLE_TIMEOUT_MS,
) -> bool:
    """Click the 'Update offset' button if available and enabled.

    Args:
        page: Playwright page object
        canvas: Canvas locator for taking screenshots
        screenshot_folder: Folder where screenshots will be saved
        timeout_ms: Timeout in milliseconds to wait after clicking

    Returns:
        True if button was clicked, False if button was not available or disabled
    """
    offset_button = page.get_by_test_id(MARKER_UPDATE_OFFSET)

    if offset_button.count() > 0:
        offset_button.scroll_into_view_if_needed()
        canvas.screenshot(path=screenshot_folder / "offset_before.png")

        # Only click if enabled
        if not offset_button.is_disabled():
            offset_button.click()
            page.wait_for_timeout(timeout_ms)
            canvas.screenshot(path=screenshot_folder / "offset_after.png")
            return True

    return False


def capture_and_verify_baseline(
    page: Page,
    canvas: Any,
    actual_screenshot_path: Path,
    reference_screenshot: Path,
) -> bytes:
    """Capture canvas screenshot and verify against reference baseline.

    Args:
        page: Playwright page object
        canvas: Canvas locator
        actual_screenshot_path: Path to save actual screenshot
        reference_screenshot: Path to reference screenshot file

    Returns:
        Screenshot bytes

    Raises:
        pytest.skip: If reference screenshot doesn't exist
        AssertionError: If screenshots don't match within tolerance
    """
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
    canvas_screenshot = canvas.screenshot(path=actual_screenshot_path)

    if reference_screenshot.exists():
        assert_screenshot_equal(actual_screenshot_path, reference_screenshot)
    else:
        pytest.skip(
            f"Reference screenshot not found: {reference_screenshot}. "
            "Run test_generate_canvas_screenshots first to generate it."
        )
    return canvas_screenshot


def verify_filter_range_label_visible(page: Page) -> None:
    """Verify that the filter range label is visible."""
    range_label = page.get_by_test_id(MARKER_FILTER_RANGE_LABEL)
    range_label.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)


def verify_canvas_matches_reference(
    canvas: Any, acceptance_test_data_folder: Path, all_tracks_filename: str
) -> None:
    """Take screenshot and verify it matches the expected baseline.

    Args:
        canvas: Canvas locator
        acceptance_test_data_folder: Path to folder with test data
        all_tracks_filename: Name of reference screenshot file

    Raises:
        pytest.skip: If reference screenshot doesn't exist
        AssertionError: If screenshots don't match within tolerance
    """
    import pytest

    new_path = acceptance_test_data_folder / "new_file.png"
    canvas.screenshot(path=new_path)

    reference_screenshot = acceptance_test_data_folder / all_tracks_filename
    if reference_screenshot.exists():
        assert_screenshot_equal(new_path, reference_screenshot)
    else:
        pytest.skip(
            f"Reference screenshot not found: {reference_screenshot}. "
            "Run test_generate_canvas_screenshots first to generate it."
        )


def reset_date_filter(page: Page) -> None:
    """Reset the date filter by clicking Reset button and unchecking checkbox."""

    filter_by_date_button = page.get_by_test_id(MARKER_FILTER_BY_DATE_BUTTON)
    filter_by_date_button.click()
    page.get_by_text("Reset").click()

    # Wait for the dialog to close (reset closes it automatically)
    page.wait_for_timeout(200)

    # Uncheck the filter checkbox to fully deactivate the filter
    filter_checkbox = page.get_by_test_id(MARKER_FILTER_BY_DATE_CHECKBOX)
    if filter_checkbox.is_checked():
        filter_checkbox.click()
        page.wait_for_timeout(200)


def verify_filter_inactive(page: Page) -> None:
    """Verify that the filter is deactivated."""
    filter_by_date_button = page.get_by_test_id(MARKER_FILTER_BY_DATE_BUTTON)
    inactive_value = filter_by_date_button.get_attribute("data-filter-by-date-active")
    assert inactive_value == "false", (
        f"Filter by date button did not indicate inactive state after reset "
        f"(value: {inactive_value})"
    )


def verify_filter_range_label_cleared(page: Page) -> None:
    """Verify that the filter range label is cleared."""
    range_label = page.get_by_test_id(MARKER_FILTER_RANGE_LABEL)
    label_text_after_reset = range_label.inner_text()
    assert (
        label_text_after_reset.strip() == ""
    ), "Date range label not cleared after reset"


def assert_screenshot_equal(
    actual: Path, expected: Path, tolerance: float = 0.01
) -> None:
    """Compare an actual screenshot with an expected screenshot file.

    Args:
        actual: Path to actual screenshot
        expected: Path to expected screenshot file
        tolerance: Acceptable difference ratio (0.0 = exact match,
        1.0 = completely different)

    Raises:
        AssertionError: If screenshots differ beyond tolerance
        FileNotFoundError: If expected screenshot file doesn't exist
    """
    assert expected.exists(), (
        f"Expected screenshot not found: {expected}\n"
        f"Generate it first using test_generate_canvas_screenshots"
    )

    actual_image = Image.open(actual)
    expected_image = Image.open(expected)

    # Check dimensions match
    assert actual_image.size == expected_image.size, (
        f"Screenshot dimensions differ: "
        f"actual {actual_image.size} vs expected {expected_image.size}"
    )

    # Compare images
    diff = ImageChops.difference(actual_image, expected_image)
    diff_stat = list(diff.getdata())

    # Calculate difference ratio
    pixels_different = sum(1 for pixel in diff_stat if pixel != (0, 0, 0))
    total_pixels = actual_image.size[0] * actual_image.size[1]
    diff_ratio = pixels_different / total_pixels if total_pixels > 0 else 0

    assert diff_ratio <= tolerance, (
        f"Screenshots differ: {diff_ratio:.2%} of pixels are different "
        f"(tolerance: {tolerance:.2%})"
    )


def get_loaded_tracks_canvas_from_otconfig(
    page: Page, rm: ResourceManager, otconfig_path: Path
) -> Any:
    """Load tracks from preconfigured .otconfig file and return canvas.

    Args:
        page: Playwright page object
        rm: ResourceManager for localized strings
        otconfig_path: Path to pre-configured .otconfig file

    Returns:
        Canvas locator ready for screenshots/verification
    """
    # Load preconfigured file with video and tracks already set up
    setup_with_preconfigured_otconfig(page, rm, otconfig_path)

    # Get canvas reference
    canvas = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).first
    canvas.wait_for(state="visible", timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT * 1000)

    # Enable "Show all tracks" layer
    checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    checkbox.scroll_into_view_if_needed()
    if not checkbox.is_checked():
        checkbox.click()
        page.wait_for_timeout(200)

    return canvas
