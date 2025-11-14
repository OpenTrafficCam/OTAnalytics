import time
from pathlib import Path
from typing import Iterable

import pytest
from playwright._impl import _errors
from playwright.sync_api import Locator, Page, expect  # type: ignore  # noqa: E402

from OTAnalytics.adapter_ui.dummy_viewmodel import SUPPORTED_VIDEO_FILE_TYPES
from OTAnalytics.application.resources.resource_manager import (
    AddVideoKeys,
    ResourceManager,
    TrackFormKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker import FOLDER_ICON
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_video_form.container import (
    MARKER_VIDEO_TABLE,
)
from OTAnalytics.plugin_ui.nicegui_gui.ui_factory import BASE_FILE_PICKER_DIRECTORY
from tests.conftest import ACCEPTANCE_TEST_WAIT_TIMEOUT, NiceGUITestServer

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


def _table_filenames(page: Page) -> list[str]:
    cells = page.locator(f'[test-id="{MARKER_VIDEO_TABLE}"] table tbody tr td')
    texts: list[str] = []
    for i in range(cells.count()):
        try:
            t = cells.nth(i).inner_text(timeout=ACCEPTANCE_TEST_WAIT_TIMEOUT).strip()
            if t:
                texts.append(t)
        except _errors.TimeoutError:
            pass
    # Filter to plausible video filenames
    return [
        t
        for t in texts
        if any(t.lower().endswith(e) for e in SUPPORTED_VIDEO_FILE_TYPES)
    ]


def _wait_for_names_present(page: Page, names: Iterable[str]) -> None:
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    names = list(names)
    while time.time() < deadline:
        listed = _table_filenames(page)
        if all(n in listed for n in names):
            return
        time.sleep(0.05)
    raise AssertionError(
        f"Timed out waiting for names to appear: {names}; "
        f"currently: {_table_filenames(page)}"
    )


def _click_table_cell_with_text(page: Page, text: str) -> None:
    cell = page.locator(
        f'[test-id="{MARKER_VIDEO_TABLE}"] table tbody tr td', has_text=text
    ).first
    cell.wait_for(state="visible")
    cell.click()


def _reset_videos_tab(page: Page, rm: ResourceManager) -> None:
    # Iteratively remove all rows if any
    for _ in range(50):
        names = _table_filenames(page)
        if not names:
            break
        name = names[0]
        try:
            _click_table_cell_with_text(page, name)
            page.get_by_text(
                rm.get(AddVideoKeys.BUTTON_REMOVE_VIDEOS), exact=True
            ).click()
            # wait until it's gone
            deadline = time.time() + 10
            while time.time() < deadline:
                if name not in _table_filenames(page):
                    break
                time.sleep(0.05)
        except Exception:
            # Best-effort cleanup only
            break


def _add_video_via_picker(page: Page, rm: ResourceManager, path: Path) -> None:
    page.get_by_text(rm.get(AddVideoKeys.BUTTON_ADD_VIDEOS), exact=True).click()
    ui_path = path.relative_to(BASE_FILE_PICKER_DIRECTORY)
    # Double-click each path segment within the file picker grid (ag-grid)
    for part in ui_path.parts:
        # Use a slightly resilient selection inside the picker grid
        _open_part(page, part)


def _open_part(page: Page, part: str) -> None:
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            cells = page.locator(".ag-cell-value", has_text=part).all()
            if not cells:
                last_cell = page.locator(".ag-cell-value").last
                last_cell.scroll_into_view_if_needed()
            for cell in cells:
                inner_text = get_raw_text(cell)
                if part == inner_text:
                    cell.wait_for(state="visible", timeout=1000)
                    cell.dblclick()
                    return
        except Exception as e:
            last_cell = page.locator(".ag-cell-value").last
            last_cell.scroll_into_view_if_needed()
            last_err = e
    if last_err:
        raise last_err
    raise AssertionError(f"Could not find table cell with text: {part}")


def get_raw_text(cell: Locator) -> str:
    return cell.inner_text().strip(FOLDER_ICON).strip()


@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_remove_single_video_after_selection(
    page: Page, external_app: NiceGUITestServer, resource_manager: ResourceManager
) -> None:
    """Playwright: Removing a single selected video from the Videos tab.

    Steps:
    - Open main page, switch to Videos tab
    - Add a single video via in-app file picker UI
    - Click on Remove and verify the video disappears from the table

    Prerequisites: pytest-playwright installed and browsers set up.
    """
    base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")  # fallback
    page.goto(base_url + ENDPOINT_MAIN_PAGE)

    # Switch to Videos tab
    page.get_by_text(resource_manager.get(TrackFormKeys.TAB_TWO), exact=True).click()

    # Ensure clean slate
    _reset_videos_tab(page, resource_manager)

    # Prepare test video path from tests/data
    data_dir = Path(__file__).parents[1] / "data"
    v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
    assert v1.exists(), f"Test video missing: {v1}"

    # Add the video
    _add_video_via_picker(page, resource_manager, v1)

    name1 = v1.name
    # Wait for the filename to appear in table
    _wait_for_names_present(page, [name1])
    # Sanity check: the table is present
    expect(page.locator(f'[test-id="{MARKER_VIDEO_TABLE}"]')).to_be_visible()

    # Remove the row
    _click_table_cell_with_text(page, name1)
    page.get_by_text(
        resource_manager.get(AddVideoKeys.BUTTON_REMOVE_VIDEOS), exact=True
    ).click()

    # Verify it's gone
    last_err: Exception | None = None
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    while time.time() < deadline:
        try:
            if name1 not in _table_filenames(page):
                break
        except Exception as e:
            last_err = e
        time.sleep(0.5)
    if last_err:
        raise last_err
    remaining = _table_filenames(page)
    assert (
        name1 not in remaining
    ), f"Video should have been removed, but still present in: {remaining}"
