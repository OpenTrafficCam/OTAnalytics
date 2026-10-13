import json
import time
from pathlib import Path
from typing import Any

import pytest
from playwright.sync_api import Page, expect  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import (
    FlowAndSectionKeys,
    ResourceManager,
    SectionKeys,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.edit_flow_dialog import (
    MARKER_NAME as MARKER_FLOW_NAME,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.edit_section_dialog import (
    MARKER_NAME as MARKER_SECTION_NAME,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import (
    MARKER_APPLY as MARKER_DIALOG_APPLY,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (
    EDIT_COLOR,
    EDIT_KNOB_ID_PREFIX,
    MARKER_INTERACTIVE_IMAGE,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.flow_form import (
    MARKER_BUTTON_GENERATE,
    MARKER_BUTTON_PROPERTIES,
    MARKER_BUTTON_REMOVE,
    MARKER_FLOW_TABLE,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.sections_form import (  # noqa
    MARKER_SECTION_TABLE,
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
    load_main_page,
    navigate_and_prepare,
    save_project_as,
    search_for_marker_element,
    setup_with_preconfigured_otconfig,
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
        # Load preconfigured file with video and tracks already set up
        load_main_page(page, external_app)

        data_dir = Path(__file__).parents[1] / "data"
        otconfig_path = data_dir / "sections_created_test_file.otconfig"
        setup_with_preconfigured_otconfig(page, resource_manager, otconfig_path)

        # Switch to Sections tab
        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_SECTION), exact=True
        ).click()

        # Create two additional sections
        names = ["First-Line", "Second-Line"]
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
        # Load preconfigured file with video, tracks, and sections already set up
        load_main_page(page, external_app)

        data_dir = Path(__file__).parents[1] / "data"
        otconfig_path = data_dir / "sections_created_test_file.otconfig"
        setup_with_preconfigured_otconfig(page, resource_manager, otconfig_path)

        # Switch to Flows tab (sections already exist from preconfigured file)
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
        # Load preconfigured file with video, tracks, and sections already set up
        load_main_page(page, external_app)

        data_dir = Path(__file__).parents[1] / "data"
        otconfig_path = data_dir / "sections_created_test_file.otconfig"
        setup_with_preconfigured_otconfig(page, resource_manager, otconfig_path)

        # Get section names from the preconfigured file
        names = ["North-Section", "South-Section"]

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


SECTION_EDITOR_SETTLE_MS = 300
NORTH_SECTION = "North-Section"


def _canvas_image(page: Page) -> Any:
    return (
        search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).locator("img").first
    )


def _to_page_position(page: Page, x: float, y: float) -> tuple[float, float]:
    """Convert image coordinates into page coordinates of the mouse."""
    image = _canvas_image(page)
    image.scroll_into_view_if_needed()
    box = image.bounding_box()
    assert box is not None, "Canvas image is not visible"
    scale = image.evaluate("element => element.clientWidth / element.naturalWidth")
    return box["x"] + x * scale, box["y"] + y * scale


def _edit_knobs(page: Page) -> Any:
    return search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).locator(
        f"svg circle[id^='{EDIT_KNOB_ID_PREFIX}']"
    )


def _move_mouse(page: Page, x: float, y: float) -> None:
    page.mouse.move(*_to_page_position(page, x, y), steps=3)
    page.wait_for_timeout(SECTION_EDITOR_SETTLE_MS)


def _click(page: Page, x: float, y: float, button: str = "left") -> None:
    page.mouse.click(*_to_page_position(page, x, y), button=button)  # type: ignore
    page.wait_for_timeout(SECTION_EDITOR_SETTLE_MS)


def _press(page: Page, key: str) -> None:
    page.keyboard.press(key)
    page.wait_for_timeout(SECTION_EDITOR_SETTLE_MS)


def _open_sections_of_preconfigured_project(
    page: Page, external_app: NiceGUITestServer, resource_manager: ResourceManager
) -> None:
    load_main_page(page, external_app)
    otconfig_path = (
        Path(__file__).parents[1] / "data" / "sections_created_test_file.otconfig"
    )
    setup_with_preconfigured_otconfig(page, resource_manager, otconfig_path)
    page.get_by_text(
        resource_manager.get(FlowAndSectionKeys.TAB_SECTION), exact=True
    ).click()
    _dismiss_notifications(page)


def _dismiss_notifications(page: Page) -> None:
    """Close notifications of loading the project, they may cover the canvas."""
    notifications = page.locator(".q-notification")
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    while notifications.count() and time.time() < deadline:
        close_buttons = notifications.locator("button")
        if close_buttons.count():
            # Notifications keep moving while others disappear, so no regular click
            close_buttons.first.dispatch_event("click")
        page.wait_for_timeout(PLAYWRIGHT_POLL_INTERVAL_SLOW_MS)
    expect(notifications).to_have_count(0)


def _edit_geometry_of(
    page: Page, resource_manager: ResourceManager, section_name: str
) -> None:
    table = search_for_marker_element(page, MARKER_SECTION_TABLE).first
    table.locator("tbody tr").filter(has_text=section_name).first.click()
    page.get_by_text(resource_manager.get(SectionKeys.BUTTON_EDIT), exact=True).click()
    expect(_edit_knobs(page)).not_to_have_count(0)


def _saved_section_coordinates(
    page: Page, resource_manager: ResourceManager, path: Path, section_name: str
) -> list[tuple[int, int]]:
    save_project_as(page, resource_manager, path)
    deadline = time.time() + ACCEPTANCE_TEST_WAIT_TIMEOUT
    while not path.exists() and time.time() < deadline:
        time.sleep(PLAYWRIGHT_POLL_INTERVAL_SLOW_MS / 1000)
    assert path.exists(), f"Expected saved configuration at {path}"
    sections = json.loads(path.read_text())["sections"]
    section = next(s for s in sections if s["name"] == section_name)
    return [(c["x"], c["y"]) for c in section["coordinates"]]


class TestSectionEditorOnCanvas:

    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_draw_line_section_with_preview_and_right_click(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
    ) -> None:
        """Draw a line section: preview follows the mouse, right click finishes."""
        _open_sections_of_preconfigured_project(page, external_app, resource_manager)
        page.get_by_text(
            resource_manager.get(SectionKeys.BUTTON_ADD_LINE), exact=True
        ).click()

        _click(page, 40, 200)
        _move_mouse(page, 200, 260)

        preview = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).locator(
            f"svg polyline[stroke='{EDIT_COLOR}']"
        )
        expect(preview).to_have_count(1)

        _click(page, 200, 260)
        _click(page, 200, 260, button="right")

        name_input = search_for_marker_element(page, MARKER_SECTION_NAME).first
        name_input.wait_for(state="visible")
        name_input.fill("Drawn-Section")
        search_for_marker_element(page, MARKER_DIALOG_APPLY).first.click()

        table = search_for_marker_element(page, MARKER_SECTION_TABLE).first
        expect(table).to_contain_text("Drawn-Section")

    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_insert_and_delete_knob_of_section(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
        test_data_tmp_dir: Path,
    ) -> None:
        """Insert a knob with '+' and delete it again with 'Delete'."""
        _open_sections_of_preconfigured_project(page, external_app, resource_manager)

        knobs = _edit_knobs(page)

        _edit_geometry_of(page, resource_manager, NORTH_SECTION)
        expect(knobs).to_have_count(2)
        _move_mouse(page, 88, 60)
        _press(page, "+")
        expect(knobs).to_have_count(3)
        _click(page, 88, 60)
        _press(page, "Enter")
        expect(knobs).to_have_count(0)

        coordinates = _saved_section_coordinates(
            page,
            resource_manager,
            test_data_tmp_dir / "inserted.otconfig",
            NORTH_SECTION,
        )
        assert len(coordinates) == 3
        assert coordinates[0] == (22, 22)
        assert coordinates[2] == (154, 66)

        _edit_geometry_of(page, resource_manager, NORTH_SECTION)
        expect(knobs).to_have_count(3)
        _click(page, *coordinates[1])
        _press(page, "Delete")
        expect(knobs).to_have_count(2)
        _press(page, "Enter")
        expect(knobs).to_have_count(0)

        coordinates = _saved_section_coordinates(
            page,
            resource_manager,
            test_data_tmp_dir / "deleted.otconfig",
            NORTH_SECTION,
        )
        assert coordinates == [(22, 22), (154, 66)]
