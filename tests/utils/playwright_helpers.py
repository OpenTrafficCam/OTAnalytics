import json
import logging
import time
from pathlib import Path
from typing import Any, Iterable

from playwright.sync_api import Error, Page, TimeoutError

from OTAnalytics.adapter_ui.dummy_viewmodel import SUPPORTED_VIDEO_FILE_TYPES
from OTAnalytics.application.resources.resource_manager import (
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
from OTAnalytics.plugin_ui.nicegui_gui.test_constants import TEST_ID
from tests.acceptance.conftest import (
    ACCEPTANCE_TEST_WAIT_TIMEOUT,
    IMPORT_VERIFY_MAX_POLLS,
    PLAYWRIGHT_POLL_INTERVAL_MS,
    PLAYWRIGHT_POLL_INTERVAL_SECONDS,
    PLAYWRIGHT_POLL_INTERVAL_SLOW_MS,
    PLAYWRIGHT_QUICK_VISIBLE_TIMEOUT_MS,
    PLAYWRIGHT_SHORT_WAIT_MS,
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
            cell = page.locator(".ag-cell-value", has_text=part).first
            cell.wait_for(state="visible", timeout=PLAYWRIGHT_QUICK_VISIBLE_TIMEOUT_MS)
            cell.dblclick()
            return
        except Exception as e:
            last_cell = page.locator(".ag-cell-value").last
            try:
                last_cell.scroll_into_view_if_needed()
            except Exception:
                pass
            last_err = e
    if last_err:
        raise last_err
    raise AssertionError(f"Could not find table cell with text: {part}")


def add_video_via_picker(page: Page, rm: ResourceManager, path: Path) -> None:
    """Open the in-app file picker and navigate to select the given video path."""
    # Prefer stable marker-based lookup; fall back to label if marker is unavailable
    search_for_marker_element(page, MARKER_VIDEO_ADD).first.click()
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
