import time
from pathlib import Path
from typing import Iterable

import pytest
from playwright.sync_api import Page, expect  # type: ignore  # noqa: E402

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
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import (
    MARKER_APPLY as MARKER_DIALOG_APPLY,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_video_form.container import (
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
            deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
            while time.time() < deadline:
                if name not in _table_filenames(page):
                    break
                time.sleep(0.05)
        except Exception:
            # Best-effort cleanup only
            break


def _add_video_via_picker(page: Page, rm: ResourceManager, path: Path) -> None:
    page.get_by_text(rm.get(AddVideoKeys.BUTTON_ADD_VIDEOS), exact=True).click()
    ui_path = path.relative_to(file_picker_directory())
    # Double-click each path segment within the file picker grid (ag-grid)
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
            last_cell = page.locator(".ag-cell-value").last
            try:
                last_cell.scroll_into_view_if_needed()
            except Exception:
                pass
            last_err = e
    if last_err:
        raise last_err
    raise AssertionError(f"Could not find table cell with text: {part}")


class TestAddLineSectionWithDialog:
    @pytest.mark.timeout(300)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_add_line_section_with_dialog(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
    ) -> None:
        """Playwright: Add a line section via canvas interaction and confirm via dialog.

        Steps:
        - Open main page, switch to Videos tab
        - Add a video via in-app file picker UI and select it to render a frame
        - Switch to Sections tab, activate "Add line", click on the interactive image
        - Enter a name in the dialog and apply
        - Verify the section name appears on the page

        Prerequisites: pytest-playwright installed and browsers set up.
        """
        base_url = getattr(
            external_app, "base_url", "http://127.0.0.1:8080"
        )  # fallback
        page.goto(base_url + ENDPOINT_MAIN_PAGE)

        # Switch to Videos tab
        page.get_by_text(
            resource_manager.get(TrackFormKeys.TAB_TWO), exact=True
        ).click()

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

        # Select the first video row to ensure preview rendering
        _click_table_cell_with_text(page, name1)

        # Go to Sections tab
        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_SECTION), exact=True
        ).click()

        # Ensure the interactive image exists and is visible; prefer inner <img>
        canvas_locator = page.locator(f'[test-id="{MARKER_INTERACTIVE_IMAGE}"]')
        expect(canvas_locator).to_be_visible()
        img = page.locator(f'[test-id="{MARKER_INTERACTIVE_IMAGE}"] img').first
        target = img if img.count() else canvas_locator
        target.scroll_into_view_if_needed()

        # Activate "Add line" tool
        try:
            page.get_by_text(
                resource_manager.get(SectionKeys.BUTTON_ADD_LINE), exact=True
            ).click()
        except Exception:
            try:
                # Fallback to marker if text lookup fails
                page.locator('[test-id="marker-button-add-line"]').first.click()
            except Exception:
                pass

        # Perform several clicks to create a simple line; finish without right-click
        for pos in [(10, 10), (120, 40), (220, 90)]:
            try:
                target.click(position={"x": pos[0], "y": pos[1]})
            except Exception:
                # Try clicking the wrapper if inner img fails
                canvas_locator.click(position={"x": pos[0], "y": pos[1]})

        # Finalize the new section with Enter (NiceGUI hotkey) to open the dialog
        page.keyboard.press("Enter")

        # Fill the section name in the dialog
        # Try input within the marker first, then fallback to the marker element itself
        name_input = page.locator(f'[test-id="{MARKER_SECTION_NAME}"] input').first
        if not name_input.count():
            name_input = page.locator(f'[test-id="{MARKER_SECTION_NAME}"]').first
        name_input.wait_for(state="visible")
        name_input.fill("Name")

        # Click Apply
        apply_button = page.locator(f'[test-id="{MARKER_DIALOG_APPLY}"]').first
        apply_button.wait_for(state="visible")
        apply_button.click()

        deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        created = False
        while time.time() < deadline and not created:
            try:
                html = page.content()
                if "Name" in html:
                    created = True
                    break
            except Exception:
                pass
            time.sleep(0.1)
        assert (
            created
        ), "Section with the specified name was not found after applying the dialog"

    @pytest.mark.timeout(450)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_add_flow_remove_flow_and_generate_flow(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
    ) -> None:
        """Playwright: Add multiple line sections via dialog and ensure all appear.

        This test repeats the section-adding interaction twice with unique names
        to verify the dialog can be used multiple times in a single session.
        """
        base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
        page.goto(base_url + ENDPOINT_MAIN_PAGE)

        # Videos tab
        page.get_by_text(
            resource_manager.get(TrackFormKeys.TAB_TWO), exact=True
        ).click()
        _reset_videos_tab(page, resource_manager)

        data_dir = Path(__file__).parents[1] / "data"
        v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        assert v1.exists(), f"Test video missing: {v1}"
        _add_video_via_picker(page, resource_manager, v1)
        _wait_for_names_present(page, [v1.name])
        _click_table_cell_with_text(page, v1.name)

        # Sections tab
        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_SECTION), exact=True
        ).click()

        canvas_locator = page.locator(f'[test-id="{MARKER_INTERACTIVE_IMAGE}"]')
        expect(canvas_locator).to_be_visible()
        img = page.locator(f'[test-id="{MARKER_INTERACTIVE_IMAGE}"] img').first
        target = img if img.count() else canvas_locator
        target.scroll_into_view_if_needed()

        def create_section(section_name: str) -> None:
            # Activate tool each time to be safe
            try:
                page.get_by_text(
                    resource_manager.get(SectionKeys.BUTTON_ADD_LINE), exact=True
                ).click()
            except Exception:
                pass
            for pos in [(20, 20), (140, 60), (260, 120)]:
                try:
                    target.click(position={"x": pos[0], "y": pos[1]})
                except Exception:
                    canvas_locator.click(position={"x": pos[0], "y": pos[1]})
            # Finalize with Enter to open the section dialog
            page.keyboard.press("Enter")
            ni = page.locator(f'[test-id="{MARKER_SECTION_NAME}"] input').first
            if not ni.count():
                ni = page.locator(f'[test-id="{MARKER_SECTION_NAME}"]').first
            ni.wait_for(state="visible")
            ni.fill(section_name)
            ab = page.locator(f'[test-id="{MARKER_DIALOG_APPLY}"]').first
            ab.wait_for(state="visible")
            ab.click()
            # Wait for the name to appear anywhere in DOM
            deadline_local = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
            while time.time() < deadline_local:
                try:
                    if section_name in page.content():
                        return
                except Exception:
                    pass
                time.sleep(0.1)
            raise AssertionError(f"Section name not found after apply: {section_name}")

        names = ["First-Line", "Second-Line"]
        for n in names:
            create_section(n)

        # Final check for sections: both names present in the DOM
        html = page.content()
        assert all(
            n in html for n in names
        ), "Not all section names are present in the page source"

        # Now switch to Flow tab and create a flow using the two sections
        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_FLOW), exact=True
        ).click()

        # Click the 'Add' flow button
        try:
            page.get_by_text(
                resource_manager.get(FlowKeys.BUTTON_ADD), exact=True
            ).click()
        except Exception:
            # Fallback to marker if text lookup fails
            page.locator('[test-id="marker-button-add"]').first.click()

        # Ensure the flow dialog opened and both section selects are visible
        page.locator(f'[test-id="{MARKER_FLOW_NAME}"]').first.wait_for(state="visible")
        page.locator(f'[test-id="{MARKER_START_SECTION}"]').first.wait_for(
            state="visible"
        )
        page.locator(f'[test-id="{MARKER_END_SECTION}"]').first.wait_for(
            state="visible"
        )
        flow_name_input = page.locator(f'[test-id="{MARKER_FLOW_NAME}"]').first
        flow_name_input.wait_for(state="visible")
        custom_flow_name = "My-Flow"
        flow_name_input.fill(custom_flow_name)
        page.locator(f'[test-id="{MARKER_END_SECTION}"]').first.click()
        page.keyboard.press("ArrowDown")  # move from first to second option
        page.keyboard.press("Enter")  # confirm selection

        # Apply the dialog
        flow_apply_btn = page.locator(f'[test-id="{MARKER_DIALOG_APPLY}"]').first
        flow_apply_btn.wait_for(state="visible")
        flow_apply_btn.click()

        # Verify that the new flow appears in the flow table or DOM
        deadline_flow = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        found_flow = False
        while time.time() < deadline_flow and not found_flow:
            try:
                # Prefer checking within the flow table if present
                table_locator = page.locator('[test-id="marker-flow-table"]')
                if (
                    table_locator.count()
                    and custom_flow_name in table_locator.inner_text()
                ):
                    found_flow = True
                    break
                if custom_flow_name in page.content():
                    found_flow = True
                    break
            except Exception:
                pass
            time.sleep(0.1)
        assert found_flow, "Flow was not created or not visible in the UI"

        # Robustly select the newly created flow in the flow table
        table = page.locator('[test-id="marker-flow-table"]').first
        table.wait_for(state="visible")
        # Prefer clicking the actual table row containing the flow name
        row = table.locator("tbody tr").filter(has_text=custom_flow_name).first
        row.wait_for(state="visible")
        row.scroll_into_view_if_needed()
        row.click()

        page.locator('[test-id="marker-button-properties"]').first.click()
        # Give the UI a short moment to process the selection
        time.sleep(0.5)

        name_input = page.locator(f'[test-id="{MARKER_FLOW_NAME}"]').first
        name_input.wait_for(state="visible")
        new_flow_name = "My-Flow-Renamed"
        name_input.fill(new_flow_name)
        # Cancel the dialog via Escape
        page.keyboard.press("Escape")
        # Wait briefly for the dialog to close
        time.sleep(0.3)
        # Validate that the flow kept its original name in the table
        table = page.locator('[test-id="marker-flow-table"]').first
        table.wait_for(state="visible")
        table_text = table.inner_text()
        assert custom_flow_name in table_text
        assert new_flow_name not in table_text
        page.locator('[test-id="marker-button-properties"]').first.click()
        # Give the UI a short moment to process the selection
        time.sleep(0.5)

        name_input = page.locator(f'[test-id="{MARKER_FLOW_NAME}"]').first
        name_input.wait_for(state="visible")
        new_flow_name = "My-Flow-Renamed"
        name_input.fill(new_flow_name)
        page.locator('[test-id="marker-apply"]').first.click()
        time.sleep(0.3)
        # Validate that the flow kept its original name in the table
        table = page.locator('[test-id="marker-flow-table"]').first
        table.wait_for(state="visible")
        table_text = table.inner_text()
        assert new_flow_name in table_text

        remove_button = page.locator('[test-id="marker-button-remove"]').first
        remove_button.wait_for(state="visible")
        remove_button.click()
        time.sleep(0.3)
        table = page.locator('[test-id="marker-flow-table"]').first
        table.wait_for(state="visible")
        table_text = table.inner_text()
        assert new_flow_name not in table_text

        generate_button = page.locator('[test-id="marker-button-generate"]').first
        generate_button.wait_for(state="visible")
        generate_button.click()

        deadline_gen = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        matched_texts: list[str] = []
        last_texts: list[str] = []
        while time.time() < deadline_gen:
            try:
                table = page.locator('[test-id="marker-flow-table"]').first
                table.wait_for(state="visible")
                rows = table.locator("tbody tr")
                last_texts = rows.all_text_contents() if rows.count() else []
                matched_texts = [t for t in last_texts if all(n in t for n in names)]
                if len(matched_texts) >= 2:
                    break
            except Exception:
                pass
            time.sleep(0.1)
        assert (
            len(matched_texts) >= 2
        ), f"Expected 2 generated flows containing both section names {names}, but got {len(matched_texts)}. Rows: {last_texts}"  # noqa
