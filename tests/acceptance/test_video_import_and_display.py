import time
from pathlib import Path

import pytest
from playwright.sync_api import Page  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import (
    AddVideoKeys,
    ResourceManager,
    TrackFormKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.container import (
    MARKER_VIDEO_TAB,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (
    MARKER_INTERACTIVE_IMAGE,
)
from tests.conftest import (
    ACCEPTANCE_TEST_PYTEST_TIMEOUT,
    ACCEPTANCE_TEST_WAIT_TIMEOUT,
    PLAYWRIGHT_POLL_INTERVAL_MS,
    NiceGUITestServer,
)
from tests.utils.playwright_helpers import (
    add_video_via_picker,
    click_table_cell_with_text,
    reset_videos_tab,
    search_for_marker_element,
    table_filenames,
    wait_for_names_present,
)

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
class TestVideoImportAndDisplay:
    def test_remove_single_video_after_selection(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
    ) -> None:
        """Playwright: Removing a single selected video from the Videos tab.

        Steps:
        - Open main page, switch to Videos tab
        - Add a single video via in-app file picker UI
        - Click on Remove and verify the video disappears from the table
        """
        base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
        page.goto(base_url + ENDPOINT_MAIN_PAGE)

        # Switch to Videos tab and ensure clean slate (prefer marker with fallback)
        try:
            search_for_marker_element(page, MARKER_VIDEO_TAB).first.click()
        except Exception:
            page.get_by_text(
                resource_manager.get(TrackFormKeys.TAB_TWO), exact=True
            ).click()
        reset_videos_tab(page, resource_manager)

        # Prepare test video path from tests/data
        data_dir = Path(__file__).parents[1] / "data"
        v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        assert v1.exists(), f"Test video missing: {v1}"

        # Add the video via in-app picker
        add_video_via_picker(page, resource_manager, v1)

        # Wait for the filename to appear in table
        name1 = v1.name
        wait_for_names_present(page, [name1])

        # Remove the row
        click_table_cell_with_text(page, name1)
        page.get_by_text(
            resource_manager.get(AddVideoKeys.BUTTON_REMOVE_VIDEOS), exact=True
        ).click()

        # Verify it's gone
        deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        while time.time() < deadline:
            if name1 not in table_filenames(page):
                break
            time.sleep(PLAYWRIGHT_POLL_INTERVAL_MS / 1000)
        remaining = table_filenames(page)
        assert (
            name1 not in remaining
        ), f"Video should have been removed, but still present in: {remaining}"

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

        # Switch to Videos tab and ensure clean slate (prefer marker with fallback)
        try:
            search_for_marker_element(page, MARKER_VIDEO_TAB).first.click()
        except Exception:
            page.get_by_text(
                resource_manager.get(TrackFormKeys.TAB_TWO), exact=True
            ).click()
        reset_videos_tab(page, resource_manager)

        data_dir = Path(__file__).parents[1] / "data"
        v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        v2 = data_dir / "Testvideo_Cars-Truck_FR20_2020-01-01_00-00-00.mp4"
        assert v1.exists() and v2.exists(), "Test videos are missing in tests/data"

        # Add both videos via in-app picker
        add_video_via_picker(page, resource_manager, v1)
        add_video_via_picker(page, resource_manager, v2)

        names = [v1.name, v2.name]
        wait_for_names_present(page, names)

        # Check sorting (alphabetical by visible filename)
        listed = table_filenames(page)
        assert listed == sorted(names), f"Expected {sorted(names)}, got {listed}"

        # Select first video and ensure preview image becomes visible and has src
        click_table_cell_with_text(page, v1.name)
        img = (
            search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE)
            .locator("img")
            .first
        )
        img.wait_for(state="visible")
        src1 = img.get_attribute("src") or ""
        assert src1, "Preview image src should not be empty after selecting first video"

        # Switch selection to second video, expect image src to change
        click_table_cell_with_text(page, v2.name)
        deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        changed = False
        while time.time() < deadline:
            src2 = img.get_attribute("src") or ""
            if src2 and src2 != src1:
                changed = True
                break
            time.sleep(PLAYWRIGHT_POLL_INTERVAL_MS / 1000)
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

        # Switch to Videos tab and clean slate (prefer marker with fallback)
        try:
            search_for_marker_element(page, MARKER_VIDEO_TAB).first.click()
        except Exception:
            page.get_by_text(
                resource_manager.get(TrackFormKeys.TAB_TWO), exact=True
            ).click()
        reset_videos_tab(page, resource_manager)

        data_dir = Path(__file__).parents[1] / "data"
        v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        v2 = data_dir / "Testvideo_Cars-Truck_FR20_2020-01-01_00-00-00.mp4"
        assert v1.exists() and v2.exists(), "Test videos are missing in tests/data"

        # Add videos
        add_video_via_picker(page, resource_manager, v1)
        add_video_via_picker(page, resource_manager, v2)
        wait_for_names_present(page, [v1.name, v2.name])

        # Remove first video
        click_table_cell_with_text(page, v1.name)
        page.get_by_text(
            resource_manager.get(AddVideoKeys.BUTTON_REMOVE_VIDEOS), exact=True
        ).click()
        # Wait gone
        deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        while time.time() < deadline:
            if v1.name not in table_filenames(page):
                break
            time.sleep(PLAYWRIGHT_POLL_INTERVAL_MS / 1000)
        assert v1.name not in table_filenames(page)

        # Remove second video
        click_table_cell_with_text(page, v2.name)
        page.get_by_text(
            resource_manager.get(AddVideoKeys.BUTTON_REMOVE_VIDEOS), exact=True
        ).click()
        deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        while time.time() < deadline:
            if v2.name not in table_filenames(page):
                break
            time.sleep(PLAYWRIGHT_POLL_INTERVAL_MS / 1000)
        assert v2.name not in table_filenames(page)
