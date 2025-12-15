import json
import time
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import (
    FileChooserDialogKeys,
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
    MARKER_FILENAME,
)
from OTAnalytics.plugin_ui.nicegui_gui.endpoints import ENDPOINT_MAIN_PAGE
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import (
    MARKER_APPLY as MARKER_DIALOG_APPLY,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (
    MARKER_INTERACTIVE_IMAGE,
)
from tests.conftest import (
    ACCEPTANCE_TEST_PYTEST_TIMEOUT,
    ACCEPTANCE_TEST_WAIT_TIMEOUT,
    PLAYWRIGHT_POLL_INTERVAL_SLOW_MS,
    NiceGUITestServer,
)
from tests.utils.playwright_helpers import (
    add_video_via_picker,
    click_table_cell_with_text,
    fill_project_information,
    reset_videos_tab,
    test_id,
    wait_for_names_present,
)

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


class TestAddLineSectionWithDialog:

    @pytest.mark.skip(reason="only works in headed right now")
    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
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
        reset_videos_tab(page, resource_manager)

        # Prepare test video path from tests/data
        data_dir = Path(__file__).parents[1] / "data"
        v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        assert v1.exists(), f"Test video missing: {v1}"

        # Add the video
        add_video_via_picker(page, resource_manager, v1)

        name1 = v1.name
        # Wait for the filename to appear in table
        wait_for_names_present(page, [name1])

        # Select the first video row to ensure preview rendering
        click_table_cell_with_text(page, name1)

        # Go to Sections tab
        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_SECTION), exact=True
        ).click()

        # Ensure the interactive image exists and is visible; prefer inner <img>
        canvas_locator = test_id(page, MARKER_INTERACTIVE_IMAGE)
        expect(canvas_locator).to_be_visible()
        img = test_id(page, MARKER_INTERACTIVE_IMAGE).locator("img").first
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
                test_id(page, "marker-button-add-line").first.click()
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
        name_input = test_id(page, MARKER_SECTION_NAME).locator("input").first
        if not name_input.count():
            name_input = test_id(page, MARKER_SECTION_NAME).first
        name_input.wait_for(state="visible")
        name_input.fill("Name")

        # Click Apply
        apply_button = test_id(page, MARKER_DIALOG_APPLY).first
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
            time.sleep(PLAYWRIGHT_POLL_INTERVAL_SLOW_MS / 1000)
        assert (
            created
        ), "Section with the specified name was not found after applying the dialog"

    def _navigate_and_prepare(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
    ) -> None:
        base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
        page.goto(base_url + ENDPOINT_MAIN_PAGE)
        fill_project_information(
            page,
            resource_manager,
            name="Test Project - Flow E2E",
            date_value="2023-05-24",
            time_value="06:00:00",
        )

    def _goto_sections_with_one_video(
        self, page: Page, resource_manager: ResourceManager
    ) -> None:
        page.get_by_text(
            resource_manager.get(TrackFormKeys.TAB_TWO), exact=True
        ).click()
        reset_videos_tab(page, resource_manager)
        data_dir = Path(__file__).parents[1] / "data"
        v1 = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        assert v1.exists(), f"Test video missing: {v1}"
        add_video_via_picker(page, resource_manager, v1)
        wait_for_names_present(page, [v1.name])
        click_table_cell_with_text(page, v1.name)
        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_SECTION), exact=True
        ).click()

    def _create_section(
        self, page: Page, resource_manager: ResourceManager, section_name: str
    ) -> None:
        canvas_locator = test_id(page, MARKER_INTERACTIVE_IMAGE)
        expect(canvas_locator).to_be_visible()
        img = test_id(page, MARKER_INTERACTIVE_IMAGE).locator("img").first
        target = img if img.count() else canvas_locator
        target.scroll_into_view_if_needed()
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
        page.keyboard.press("Enter")
        ni = test_id(page, MARKER_SECTION_NAME).locator("input").first
        if not ni.count():
            ni = test_id(page, MARKER_SECTION_NAME).first
        ni.wait_for(state="visible")
        ni.fill(section_name)
        ab = test_id(page, MARKER_DIALOG_APPLY).first
        ab.wait_for(state="visible")
        ab.click()
        deadline_local = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        while time.time() < deadline_local:
            try:
                if section_name in page.content():
                    return
            except Exception:
                pass
            time.sleep(PLAYWRIGHT_POLL_INTERVAL_SLOW_MS / 1000)
        raise AssertionError(f"Section name not found after apply: {section_name}")

    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_create_sections_two_times(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
    ) -> None:
        self._navigate_and_prepare(page, external_app, resource_manager)
        self._goto_sections_with_one_video(page, resource_manager)
        names = ["First-Line", "Second-Line"]
        for n in names:
            self._create_section(page, resource_manager, n)
        html = page.content()
        assert all(n in html for n in names)

    @pytest.mark.skip(reason="only works in headed right now")
    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_create_and_rename_flow_from_sections(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
    ) -> None:
        self._navigate_and_prepare(page, external_app, resource_manager)
        self._goto_sections_with_one_video(page, resource_manager)
        for n in ["First-Line", "Second-Line"]:
            self._create_section(page, resource_manager, n)
        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_FLOW), exact=True
        ).click()
        try:
            page.get_by_text(
                resource_manager.get(FlowKeys.BUTTON_ADD), exact=True
            ).click()
        except Exception:
            test_id(page, "marker-button-add").first.click()
        test_id(page, MARKER_FLOW_NAME).first.wait_for(state="visible")
        test_id(page, MARKER_START_SECTION).first.wait_for(state="visible")
        test_id(page, MARKER_END_SECTION).first.wait_for(state="visible")
        flow_name_input = test_id(page, MARKER_FLOW_NAME).first
        custom_flow_name = "My-Flow"
        flow_name_input.fill(custom_flow_name)
        # Select start section (ensure both start and end are chosen)
        test_id(page, MARKER_START_SECTION).first.click()
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        # Select end section
        test_id(page, MARKER_END_SECTION).first.click()
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        test_id(page, MARKER_DIALOG_APPLY).first.click()
        table = test_id(page, "marker-flow-table").first
        table.wait_for(state="visible")
        # Wait until the table contains the newly created flow name
        deadline_flow = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        while time.time() < deadline_flow:
            try:
                if custom_flow_name in table.inner_text():
                    break
            except Exception:
                pass
            time.sleep(PLAYWRIGHT_POLL_INTERVAL_SLOW_MS / 1000)
        assert custom_flow_name in table.inner_text()
        row = table.locator("tbody tr").filter(has_text=custom_flow_name).first
        row.click()
        test_id(page, "marker-button-properties").first.click()
        name_input = test_id(page, MARKER_FLOW_NAME).first
        new_flow_name = "My-Flow-Renamed"
        name_input.fill(new_flow_name)
        page.keyboard.press("Escape")
        time.sleep(2 * PLAYWRIGHT_POLL_INTERVAL_SLOW_MS / 1000)
        assert custom_flow_name in table.inner_text()
        assert new_flow_name not in table.inner_text()
        test_id(page, "marker-button-properties").first.click()
        name_input = test_id(page, MARKER_FLOW_NAME).first
        name_input.fill(new_flow_name)
        test_id(page, "marker-apply").first.click()
        time.sleep(2 * PLAYWRIGHT_POLL_INTERVAL_SLOW_MS / 1000)
        assert new_flow_name in table.inner_text()

    @pytest.mark.skip(reason="only works in headed right now")
    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_remove_flow_and_generate_flows_and_save_project(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
        test_data_tmp_dir: Path,
    ) -> None:
        # Prepare and create sections
        self._navigate_and_prepare(page, external_app, resource_manager)
        self._goto_sections_with_one_video(page, resource_manager)
        names = ["First-Line", "Second-Line"]
        for n in names:
            self._create_section(page, resource_manager, n)

        # Create one flow then remove it
        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_FLOW), exact=True
        ).click()
        try:
            page.get_by_text(
                resource_manager.get(FlowKeys.BUTTON_ADD), exact=True
            ).click()
        except Exception:
            test_id(page, "marker-button-add").first.click()
        test_id(page, MARKER_FLOW_NAME).first.fill("Temp-Flow")
        # Select start and end sections before applying
        test_id(page, MARKER_START_SECTION).first.click()
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        test_id(page, MARKER_END_SECTION).first.click()
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        test_id(page, MARKER_DIALOG_APPLY).first.click()
        table = test_id(page, "marker-flow-table").first
        table.wait_for(state="visible")
        # Wait until the table contains the newly created flow
        deadline_temp = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        while time.time() < deadline_temp:
            try:
                if "Temp-Flow" in table.inner_text():
                    break
            except Exception:
                pass
            time.sleep(PLAYWRIGHT_POLL_INTERVAL_SLOW_MS / 1000)
        assert "Temp-Flow" in table.inner_text()
        row = table.locator("tbody tr").filter(has_text="Temp-Flow").first
        row.click()
        test_id(page, "marker-button-remove").first.click()
        time.sleep(2 * PLAYWRIGHT_POLL_INTERVAL_SLOW_MS / 1000)
        assert "Temp-Flow" not in table.inner_text()

        # Generate flows from sections and assert at least two are created
        test_id(page, "marker-button-generate").first.click()
        deadline_gen = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
        matched_texts: list[str] = []
        last_texts: list[str] = []
        while time.time() < deadline_gen:
            try:
                rows = table.locator("tbody tr")
                last_texts = rows.all_text_contents() if rows.count() else []
                matched_texts = [t for t in last_texts if all(n in t for n in names)]
                if len(matched_texts) >= 2:
                    break
            except Exception:
                pass
            time.sleep(PLAYWRIGHT_POLL_INTERVAL_SLOW_MS / 1000)
        assert (
            len(matched_texts) >= 2
        ), f"Expected >=2 generated flows with {names}, got {len(matched_texts)}: {last_texts}"  # noqa

        # Save project and compare with reference
        test_id(page, "marker-project-save-as").first.click()
        test_id(page, MARKER_DIALOG_APPLY).first.wait_for(state="visible")
        dir_label = resource_manager.get(FileChooserDialogKeys.LABEL_DIRECTORY)
        page.get_by_label(dir_label, exact=True).fill(str(test_data_tmp_dir))
        test_id(page, MARKER_FILENAME).first.fill("test_name")
        test_id(page, MARKER_DIALOG_APPLY).first.click()
        saved_path = test_data_tmp_dir / "test_name.otconfig"
        assert saved_path.exists(), f"Expected saved configuration at {saved_path}"
        reference_path = Path(__file__).parents[1] / "data" / "test_name.otconfig"
        with (
            saved_path.open("r", encoding="utf-8") as fa,
            reference_path.open("r", encoding="utf-8") as fb,
        ):
            ja = json.load(fa)
            jb = json.load(fb)
        assert ja == jb, "Saved configuration does not match reference file"
