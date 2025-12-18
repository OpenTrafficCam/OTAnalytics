import time
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import (
    FlowAndSectionKeys,
    FlowKeys,
    ResourceManager,
    SectionKeys,
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
    compare_json_files,
    go_to_sections_with_one_video,
    navigate_and_prepare,
    save_project_as,
    search_for_marker_element,
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
        # Use helpers for navigation and preparing one video, then go to Sections
        navigate_and_prepare(page, external_app, resource_manager)
        go_to_sections_with_one_video(page, resource_manager)

        # Use the refactored helper to create the section (includes assertions)
        self._create_section(page, resource_manager, "Name")

    def _create_section(
        self,
        page: Page,
        resource_manager: ResourceManager,
        section_name: str = "Name",
        positions: list[tuple[int, int]] = [(20, 20), (140, 60), (260, 120)],
    ) -> None:
        canvas_locator = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE)
        expect(canvas_locator).to_be_visible()
        img = (
            search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE)
            .locator("img")
            .first
        )
        target = img if img.count() else canvas_locator
        target.scroll_into_view_if_needed()
        try:
            page.get_by_text(
                resource_manager.get(SectionKeys.BUTTON_ADD_LINE), exact=True
            ).click()
        except Exception:
            pass
        for pos in positions:
            try:
                target.click(position={"x": pos[0], "y": pos[1]})
            except Exception:
                canvas_locator.click(position={"x": pos[0], "y": pos[1]})
        page.keyboard.press("Enter")
        ni = search_for_marker_element(page, MARKER_SECTION_NAME).locator("input").first
        if not ni.count():
            ni = search_for_marker_element(page, MARKER_SECTION_NAME).first
        ni.wait_for(state="visible")
        ni.fill(section_name)
        ab = search_for_marker_element(page, MARKER_DIALOG_APPLY).first
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
        navigate_and_prepare(page, external_app, resource_manager)
        go_to_sections_with_one_video(page, resource_manager)
        names = ["First-Line", "Second-Line"]
        # Use different coordinates for each created section
        coords = [
            [(20, 20), (140, 60)],
            [(220, 80), (340, 140)],
        ]
        for i, n in enumerate(names):
            self._create_section(
                page, resource_manager, n, positions=coords[i % len(coords)]
            )
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
        navigate_and_prepare(page, external_app, resource_manager)
        go_to_sections_with_one_video(page, resource_manager)
        names = ["First-Line", "Second-Line"]
        # Use different coordinates for each created section
        coords = [
            [(20, 20), (140, 60)],
            [(220, 80), (340, 140)],
        ]
        for i, n in enumerate(names):
            self._create_section(
                page, resource_manager, n, positions=coords[i % len(coords)]
            )
        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_FLOW), exact=True
        ).click()
        try:
            page.get_by_text(
                resource_manager.get(FlowKeys.BUTTON_ADD), exact=True
            ).click()
        except Exception:
            search_for_marker_element(page, "marker-button-add").first.click()
        search_for_marker_element(page, MARKER_FLOW_NAME).first.wait_for(
            state="visible"
        )
        search_for_marker_element(page, MARKER_START_SECTION).first.wait_for(
            state="visible"
        )
        search_for_marker_element(page, MARKER_END_SECTION).first.wait_for(
            state="visible"
        )
        flow_name_input = search_for_marker_element(page, MARKER_FLOW_NAME).first
        custom_flow_name = "My-Flow"
        flow_name_input.fill(custom_flow_name)
        # Select start section (ensure both start and end are chosen)
        search_for_marker_element(page, MARKER_START_SECTION).first.click()
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        # Select end section
        search_for_marker_element(page, MARKER_END_SECTION).first.click()
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        search_for_marker_element(page, MARKER_DIALOG_APPLY).first.click()
        table = search_for_marker_element(page, "marker-flow-table").first
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
        search_for_marker_element(page, "marker-button-properties").first.click()
        name_input = search_for_marker_element(page, MARKER_FLOW_NAME).first
        new_flow_name = "My-Flow-Renamed"
        name_input.fill(new_flow_name)
        page.keyboard.press("Escape")
        time.sleep(2 * PLAYWRIGHT_POLL_INTERVAL_SLOW_MS / 1000)
        assert custom_flow_name in table.inner_text()
        assert new_flow_name not in table.inner_text()
        search_for_marker_element(page, "marker-button-properties").first.click()
        name_input = search_for_marker_element(page, MARKER_FLOW_NAME).first
        name_input.fill(new_flow_name)
        search_for_marker_element(page, MARKER_DIALOG_APPLY).first.click()
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
        navigate_and_prepare(page, external_app, resource_manager)
        go_to_sections_with_one_video(page, resource_manager)
        names = ["First-Line", "Second-Line"]
        # Use different coordinates for each created section
        coords = [
            [(20, 20), (140, 60)],
            [(220, 80), (340, 140)],
        ]
        for i, n in enumerate(names):
            self._create_section(
                page, resource_manager, n, positions=coords[i % len(coords)]
            )

        # Create one flow then remove it
        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_FLOW), exact=True
        ).click()
        try:
            page.get_by_text(
                resource_manager.get(FlowKeys.BUTTON_ADD), exact=True
            ).click()
        except Exception:
            search_for_marker_element(page, "marker-button-add").first.click()
        search_for_marker_element(page, MARKER_FLOW_NAME).first.fill("Temp-Flow")
        # Select start and end sections before applying
        search_for_marker_element(page, MARKER_START_SECTION).first.click()
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        search_for_marker_element(page, MARKER_END_SECTION).first.click()
        page.keyboard.press("ArrowDown")
        page.keyboard.press("Enter")
        search_for_marker_element(page, MARKER_DIALOG_APPLY).first.click()
        table = search_for_marker_element(page, "marker-flow-table").first
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
        search_for_marker_element(page, "marker-button-remove").first.click()
        time.sleep(2 * PLAYWRIGHT_POLL_INTERVAL_SLOW_MS / 1000)
        assert "Temp-Flow" not in table.inner_text()

        # Generate flows from sections and assert at least two are created
        search_for_marker_element(page, "marker-button-generate").first.click()
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

        # Save project using shared helper and compare with reference
        save_project_as(
            page, resource_manager, test_data_tmp_dir / "test_name.otconfig"
        )
        saved_path = test_data_tmp_dir / "test_name.otconfig"
        assert saved_path.exists(), f"Expected saved configuration at {saved_path}"
        reference_path = Path(__file__).parents[1] / "data" / "test_name.otconfig"
        compare_json_files(saved_path, reference_path)
