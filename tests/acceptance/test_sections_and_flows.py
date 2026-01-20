import time
from pathlib import Path

import pytest
from playwright.sync_api import Page  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import (
    FlowAndSectionKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.edit_flow_dialog import (
    MARKER_NAME as MARKER_FLOW_NAME,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import (
    MARKER_APPLY as MARKER_DIALOG_APPLY,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.flow_form import (
    MARKER_BUTTON_GENERATE,
    MARKER_BUTTON_PROPERTIES,
    MARKER_BUTTON_REMOVE,
    MARKER_FLOW_TABLE,
)
from tests.acceptance.conftest import (
    ACCEPTANCE_TEST_FINAL_TIMEOUT_MS,
    ACCEPTANCE_TEST_PYTEST_TIMEOUT,
    ACCEPTANCE_TEST_WAIT_TIMEOUT,
    PLAYWRIGHT_POLL_INTERVAL_SLOW_MS,
    NiceGUITestServer,
)
from tests.utils.playwright_helpers import (
    compare_json_files,
    create_flow,
    create_section,
    go_to_sections_with_one_video,
    navigate_and_prepare,
    save_project_as,
    search_for_marker_element,
    wait_for_flow_present,
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

        # Use the shared helper to create the section (includes assertions)
        create_section(page, resource_manager, "Name")

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
            create_section(page, resource_manager, n, positions=coords[i % len(coords)])
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
            create_section(page, resource_manager, n, positions=coords[i % len(coords)])
        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_FLOW), exact=True
        ).click()

        custom_flow_name = "My-Flow"
        create_flow(page, resource_manager, custom_flow_name)
        wait_for_flow_present(page, custom_flow_name)

        table = search_for_marker_element(page, MARKER_FLOW_TABLE).first
        assert custom_flow_name in table.inner_text()
        row = table.locator("tbody tr").filter(has_text=custom_flow_name).first
        row.click()
        search_for_marker_element(page, MARKER_BUTTON_PROPERTIES).first.click()
        name_input = search_for_marker_element(page, MARKER_FLOW_NAME).first
        new_flow_name = "My-Flow-Renamed"
        name_input.fill(new_flow_name)
        page.keyboard.press("Escape")
        time.sleep(ACCEPTANCE_TEST_FINAL_TIMEOUT_MS)
        assert custom_flow_name in table.inner_text()
        assert new_flow_name not in table.inner_text()
        search_for_marker_element(page, MARKER_BUTTON_PROPERTIES).first.click()
        name_input = search_for_marker_element(page, MARKER_FLOW_NAME).first
        name_input.fill(new_flow_name)
        search_for_marker_element(page, MARKER_DIALOG_APPLY).first.click()
        time.sleep(2 * PLAYWRIGHT_POLL_INTERVAL_SLOW_MS)
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
            create_section(page, resource_manager, n, positions=coords[i % len(coords)])

        # Switch to Flows tab
        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_FLOW), exact=True
        ).click()

        # Create one flow then remove it
        temp_flow_name = "Temp-Flow"
        create_flow(page, resource_manager, temp_flow_name)
        wait_for_flow_present(page, temp_flow_name)

        table = search_for_marker_element(page, MARKER_FLOW_TABLE).first
        row = table.locator("tbody tr").filter(has_text=temp_flow_name).first
        row.click()
        search_for_marker_element(page, MARKER_BUTTON_REMOVE).first.click()
        time.sleep(2 * PLAYWRIGHT_POLL_INTERVAL_SLOW_MS)
        assert temp_flow_name not in table.inner_text()

        # Generate flows from sections and assert at least two are created
        search_for_marker_element(page, MARKER_BUTTON_GENERATE).first.click()
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
            time.sleep(PLAYWRIGHT_POLL_INTERVAL_SLOW_MS)
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
