import time
from pathlib import Path

import pytest
from playwright.sync_api import Page  # type: ignore  # noqa: E402

from OTAnalytics.adapter_ui.dummy_viewmodel import SUPPORTED_VIDEO_FILE_TYPES
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.container import (
    MARKER_TAB_VIDEOS,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_video_form.container import (
    MARKER_ADD_VIDEOS_BUTTON,
    MARKER_REMOVE_VIDEOS_BUTTON,
    MARKER_VIDEO_TABLE,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (
    MARKER_INTERACTIVE_IMAGE,
)
from tests.conftest import ACCEPTANCE_TEST_WAIT_TIMEOUT, NiceGUITestServer
from tests.utils.builders.otanalytics_builders import file_picker_directory

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


def _table_filenames(page: Page) -> list[str]:
    cells = page.locator(f'[test-id="{MARKER_VIDEO_TABLE}"] table tbody tr td')
    texts = [text.strip() for text in cells.all_inner_texts()]
    return [
        t
        for t in texts
        if any(t.lower().endswith(e) for e in SUPPORTED_VIDEO_FILE_TYPES)
    ]


def _wait_for_names_present(page: Page, names: list[str]) -> None:
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    while time.time() < deadline:
        listed = _table_filenames(page)
        if all(n in listed for n in names):
            return
        time.sleep(0.05)
    raise AssertionError(
        f"Timed out waiting for names to appear: {names}; currently: {_table_filenames(page)}"  # noqa
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
            page.locator(f'[test-id="{MARKER_REMOVE_VIDEOS_BUTTON}"]').first.click()
            # wait until it's gone
            deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
            while time.time() < deadline:
                if name not in _table_filenames(page):
                    break
                time.sleep(0.05)
        except Exception:
            break


def _add_video_via_picker(page: Page, rm: ResourceManager, path: Path) -> None:
    page.locator(f'[test-id="{MARKER_ADD_VIDEOS_BUTTON}"]').first.click()
    ui_path = path.relative_to(file_picker_directory())
    for part in ui_path.parts:
        _open_part(page, part)


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


@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
class TestVideoImportAndDisplayPlaywright:
    def test_add_videos_import_sort_and_display_first_frame(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
    ) -> None:
        """Playwright: Add two videos, verify sorting and preview image updates.

        Mirrors tests in TestVideoImportAndDisplay (Selenium-based).
        """
        base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
        page.goto(base_url + ENDPOINT_MAIN_PAGE)

        # Switch to Videos tab and ensure clean slate
        page.locator(f'[test-id="{MARKER_TAB_VIDEOS}"]').first.click()
        _reset_videos_tab(page, resource_manager)

        data_dir = Path(__file__).parents[1] / "data"
        v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        v2 = data_dir / "Testvideo_Cars-Truck_FR20_2020-01-01_00-00-00.mp4"
        assert v1.exists() and v2.exists(), "Test videos are missing in tests/data"

        # Add both videos via in-app picker
        _add_video_via_picker(page, resource_manager, v1)
        _add_video_via_picker(page, resource_manager, v2)

        names = [v1.name, v2.name]
        _wait_for_names_present(page, names)

        # Check sorting (alphabetical by visible filename)
        listed = _table_filenames(page)
        assert listed == sorted(names), f"Expected {sorted(names)}, got {listed}"

        # Select first video and ensure preview image becomes visible and has src
        _click_table_cell_with_text(page, v1.name)
        img = page.locator(f'[test-id="{MARKER_INTERACTIVE_IMAGE}"] img').first
        img.wait_for(state="visible")
        src1 = img.get_attribute("src") or ""
        assert src1, "Preview image src should not be empty after selecting first video"

        # Switch selection to second video, expect image src to change
        _click_table_cell_with_text(page, v2.name)
        deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        changed = False
        while time.time() < deadline:
            src2 = img.get_attribute("src") or ""
            if src2 and src2 != src1:
                changed = True
                break
            time.sleep(0.05)
        assert changed, "Preview image src should change after selecting another video"

    def test_remove_multiple_videos_after_selection(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
    ) -> None:
        """Playwright: Remove two videos sequentially (single-select table)."""
        base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
        page.goto(base_url + ENDPOINT_MAIN_PAGE)

        # Switch to Videos tab and clean slate
        page.locator(f'[test-id="{MARKER_TAB_VIDEOS}"]').first.click()
        _reset_videos_tab(page, resource_manager)

        data_dir = Path(__file__).parents[1] / "data"
        v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        v2 = data_dir / "Testvideo_Cars-Truck_FR20_2020-01-01_00-00-00.mp4"
        assert v1.exists() and v2.exists(), "Test videos are missing in tests/data"

        # Add videos
        _add_video_via_picker(page, resource_manager, v1)
        _add_video_via_picker(page, resource_manager, v2)
        _wait_for_names_present(page, [v1.name, v2.name])

        # Remove first video
        _click_table_cell_with_text(page, v1.name)
        page.locator(f'[test-id="{MARKER_REMOVE_VIDEOS_BUTTON}"]').first.click()
        # Wait gone
        deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        while time.time() < deadline:
            if v1.name not in _table_filenames(page):
                break
            time.sleep(0.05)
        assert v1.name not in _table_filenames(page)

        # Remove second video
        _click_table_cell_with_text(page, v2.name)
        page.locator(f'[test-id="{MARKER_REMOVE_VIDEOS_BUTTON}"]').first.click()
        deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        while time.time() < deadline:
            if v2.name not in _table_filenames(page):
                break
            time.sleep(0.05)
        assert v2.name not in _table_filenames(page)
