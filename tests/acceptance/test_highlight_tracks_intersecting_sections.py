"""Acceptance test: Highlight tracks intersecting/not intersecting sections.

This test verifies the functionality of highlighting tracks based on their
intersection relationship with selected sections in the visualization canvas.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.container import (
    MARKER_TAB_FLOW,
    MARKER_TAB_SECTION,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.flow_form import (
    MARKER_FLOW_TABLE,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.sections_form import (  # noqa
    MARKER_SECTION_TABLE,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
    MARKER_UPDATE_FLOW_HIGHLIGHTING,
)
from OTAnalytics.plugin_ui.visualization.visualization import (
    ASSIGNED_TO_FLOWS,
    INTERSECTING_SECTIONS,
    NOT_ASSIGNED_TO_FLOWS,
    NOT_INTERSECTING_SECTIONS,
)
from tests.acceptance.conftest import (
    ACCEPTANCE_TEST_PYTEST_TIMEOUT,
    PLAYWRIGHT_VISIBLE_TIMEOUT_MS,
    NiceGUITestServer,
)
from tests.utils.playwright_helpers import (
    get_loaded_tracks_canvas_from_otconfig,
    load_main_page,
    search_for_marker_element,
    wait_for_canvas_change,
)

# Ensure pytest-playwright is available; otherwise skip this module
playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_highlight_tracks_intersecting_sections(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """Test highlighting tracks that intersect selected sections.

    Test Steps:
    1. Load a pre-configured project with sections
    2. Click on "Highlight tracks intersecting sections" checkbox
    3. Select one section (e.g., section 1)
    4. Verify tracks intersecting section 1 are highlighted (canvas changes)
    5. Select another section (e.g., section 2)
    6. Verify tracks intersecting section 2 are highlighted (canvas changes)
    7. Click on "Highlight tracks intersecting sections" checkbox again
    8. Verify no trajectories are shown (canvas returns to baseline)

    Expected Results:
    - Checkbox can be toggled on and off
    - Canvas updates when sections are selected
    - Different sections show different highlighted tracks
    - Turning off the checkbox removes all highlighted tracks
    """
    # Setup: Load tracks with preconfigured file that includes sections
    load_main_page(page, external_app)
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"
    canvas = get_loaded_tracks_canvas_from_otconfig(
        page, resource_manager, otconfig_path
    )

    # Turn off "Show all tracks" if it's on to get clean baseline
    all_tracks_text = "All"
    all_tracks_checkbox = page.get_by_text(all_tracks_text, exact=True).nth(0)
    if all_tracks_checkbox.is_checked():
        all_tracks_checkbox.click()
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Capture baseline (no highlighting)
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
    canvas_baseline = canvas.screenshot()

    # Step 1: Enable "Highlight tracks intersecting sections" checkbox
    intersecting_checkbox = page.get_by_text(INTERSECTING_SECTIONS, exact=True).nth(0)
    intersecting_checkbox.scroll_into_view_if_needed()
    intersecting_checkbox.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Step 2: Navigate to Sections tab to select sections
    search_for_marker_element(page, MARKER_TAB_SECTION).first.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Get section table reference
    section_table = search_for_marker_element(page, MARKER_SECTION_TABLE).first
    section_table.wait_for(state="visible")

    # Step 3: Select first section from the section table
    first_section_row = section_table.locator("table tbody tr").first
    first_section_row.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify canvas changed (tracks intersecting section 1 are highlighted)
    canvas_after_section1 = wait_for_canvas_change(page, canvas, canvas_baseline)

    # Step 4: Select second section from the section table
    second_section_row = section_table.locator("table tbody tr").nth(1)
    second_section_row.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify canvas changed again (tracks intersecting section 2 are highlighted)
    canvas_after_section2 = wait_for_canvas_change(page, canvas, canvas_after_section1)

    # Step 5: Click on "Highlight tracks intersecting sections" again to turn it off
    intersecting_checkbox.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify canvas changed back (no trajectories should be shown)
    wait_for_canvas_change(page, canvas, canvas_after_section2)


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_highlight_tracks_not_intersecting_sections(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """Test highlighting tracks that do NOT intersect selected sections.

    Test Steps:
    1. Load a pre-configured project with sections
    2. Click on "Highlight tracks not intersecting sections" checkbox
    3. Select one section (e.g., section 1)
    4. Verify tracks NOT intersecting section 1 are highlighted (canvas changes)
    5. Select another section (e.g., section 2)
    6. Verify tracks NOT intersecting section 2 are highlighted (canvas changes)
    7. Click on "Highlight tracks not intersecting sections" checkbox again
    8. Verify no trajectories are shown (canvas returns to baseline)

    Expected Results:
    - Checkbox can be toggled on and off
    - Canvas updates when sections are selected
    - Different sections show different highlighted tracks (inverse of intersecting)
    - Turning off the checkbox removes all highlighted tracks
    """
    # Setup: Load tracks with preconfigured file that includes sections
    load_main_page(page, external_app)
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"
    canvas = get_loaded_tracks_canvas_from_otconfig(
        page, resource_manager, otconfig_path
    )

    # Turn off "Show all tracks" if it's on to get clean baseline
    all_tracks_text = "All"
    all_tracks_checkbox = page.get_by_text(all_tracks_text, exact=True).nth(0)
    if all_tracks_checkbox.is_checked():
        all_tracks_checkbox.click()
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Capture baseline (no highlighting)
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
    canvas_baseline = canvas.screenshot()

    # Step 1: Enable "Highlight tracks not intersecting sections" checkbox
    not_intersecting_checkbox = page.get_by_text(
        NOT_INTERSECTING_SECTIONS, exact=True
    ).nth(0)
    not_intersecting_checkbox.scroll_into_view_if_needed()
    not_intersecting_checkbox.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Step 2: Navigate to Sections tab to select sections
    search_for_marker_element(page, MARKER_TAB_SECTION).first.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Get section table reference
    section_table = search_for_marker_element(page, MARKER_SECTION_TABLE).first
    section_table.wait_for(state="visible")

    # Step 3: Select first section from the section table
    first_section_row = section_table.locator("table tbody tr").first
    first_section_row.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify canvas changed (tracks NOT intersecting section 1 are highlighted)
    canvas_after_section1 = wait_for_canvas_change(page, canvas, canvas_baseline)

    # Step 4: Select second section from the section table
    second_section_row = section_table.locator("table tbody tr").nth(1)
    second_section_row.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify canvas changed again (tracks NOT intersecting section 2 are highlighted)
    canvas_after_section2 = wait_for_canvas_change(page, canvas, canvas_after_section1)

    # Step 5: Click on "Highlight tracks not intersecting sections" again to turn it off
    not_intersecting_checkbox.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify canvas changed back (no trajectories should be shown)
    wait_for_canvas_change(page, canvas, canvas_after_section2)


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_highlight_tracks_assigned_to_flows(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """Test highlighting tracks that are assigned to selected flows.

    Test Steps:
    1. Load a pre-configured project with flows
    2. Click on "Highlight tracks assigned to flows" checkbox
    3. Show "Flows" Tab by clicking on "Flows"
    4. Select one flow (e.g., section 1 --> section 2)
    5. Verify no tracks are highlighted (flow highlighting not yet updated)
    6. Assign tracks to flows by clicking on "Update Flow Highlighting"
    7. Verify tracks assigned to flow "section 1 --> section 2" are highlighted
    8. Select another flow (e.g., section 1 --> section 3)
    9. Verify tracks assigned to flow "section 1 --> section 3" are highlighted
    10. Click on "Highlight tracks assigned to flows" checkbox again
    11. Verify no trajectories are shown (canvas returns to baseline)

    Expected Results:
    - Checkbox can be toggled on and off
    - Canvas only shows highlights after "Update Flow Highlighting" is clicked
    - Canvas updates when different flows are selected
    - Different flows show different highlighted tracks
    - Turning off the checkbox removes all highlighted tracks
    """
    # Setup: Load tracks with preconfigured file that includes flows
    load_main_page(page, external_app)
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"
    canvas = get_loaded_tracks_canvas_from_otconfig(
        page, resource_manager, otconfig_path
    )

    # Turn off "Show all tracks" if it's on to get clean baseline
    all_tracks_text = "All"
    all_tracks_checkbox = page.get_by_text(all_tracks_text, exact=True).nth(0)
    if all_tracks_checkbox.is_checked():
        all_tracks_checkbox.click()
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Capture baseline (no highlighting)
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
    canvas_baseline = canvas.screenshot()

    # Step 1: Enable "Highlight tracks assigned to flows" checkbox
    assigned_to_flows_checkbox = page.get_by_text(ASSIGNED_TO_FLOWS, exact=True).nth(0)
    assigned_to_flows_checkbox.scroll_into_view_if_needed()
    assigned_to_flows_checkbox.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Step 2: Navigate to Flows tab to select flows
    search_for_marker_element(page, MARKER_TAB_FLOW).first.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Get flow table reference
    flow_table = search_for_marker_element(page, MARKER_FLOW_TABLE).first
    flow_table.wait_for(state="visible")

    # Step 3: Select first flow from the flow table
    first_flow_row = flow_table.locator("table tbody tr").first
    first_flow_row.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Step 4: Verify no tracks are highlighted yet (canvas should not change)
    # Because flow highlighting has not been updated yet
    current_canvas = canvas.screenshot()
    assert (
        current_canvas == canvas_baseline
    ), "Canvas should not change before updating flow highlighting"

    # Step 5: Click "Update Flow Highlighting" button
    update_flow_button = search_for_marker_element(
        page, MARKER_UPDATE_FLOW_HIGHLIGHTING
    ).first
    update_flow_button.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Step 6: Verify canvas changed (tracks assigned to first flow are highlighted)
    canvas_after_flow1 = wait_for_canvas_change(page, canvas, canvas_baseline)

    # Step 7: Select second flow from the flow table (if exists)
    second_flow_row = flow_table.locator("table tbody tr").nth(1)
    if second_flow_row.count() > 0:
        second_flow_row.click()
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

        # Verify canvas changed again (tracks assigned to second flow are highlighted)
        canvas_after_flow2 = wait_for_canvas_change(page, canvas, canvas_after_flow1)
    else:
        # If only one flow exists, use the current state
        canvas_after_flow2 = canvas_after_flow1

    # Step 8: Click on "Highlight tracks assigned to flows" again to turn it off
    assigned_to_flows_checkbox.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify canvas changed back (no trajectories should be shown)
    wait_for_canvas_change(page, canvas, canvas_after_flow2)


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_highlight_tracks_not_assigned_to_flows(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """Test highlighting tracks that are NOT assigned to selected flows.

    Test Steps:
    1. Load a pre-configured project with flows
    2. Click on "Highlight tracks not assigned to flows" checkbox
    3. Show "Flows" Tab by clicking on "Flows"
    4. Select one flow (e.g., section 1 --> section 2)
    5. Verify no tracks are highlighted (flow highlighting not yet updated)
    6. Assign tracks to flows by clicking on "Update Flow Highlighting"
    7. Verify tracks NOT assigned to flow "section 1 --> section 2" are highlighted
    8. Select another flow (e.g., section 1 --> section 3)
    9. Verify tracks NOT assigned to flow "section 1 --> section 3" are highlighted
    10. Click on "Highlight tracks not assigned to flows" checkbox again
    11. Verify no trajectories are shown (canvas returns to baseline)

    Expected Results:
    - Checkbox can be toggled on and off
    - Canvas only shows highlights after "Update Flow Highlighting" is clicked
    - Canvas updates when different flows are selected
    - Different flows show different highlighted tracks (inverse of assigned)
    - Turning off the checkbox removes all highlighted tracks
    """
    # Setup: Load tracks with preconfigured file that includes flows
    load_main_page(page, external_app)
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"
    canvas = get_loaded_tracks_canvas_from_otconfig(
        page, resource_manager, otconfig_path
    )

    # Turn off "Show all tracks" if it's on to get clean baseline
    all_tracks_text = "All"
    all_tracks_checkbox = page.get_by_text(all_tracks_text, exact=True).nth(0)
    if all_tracks_checkbox.is_checked():
        all_tracks_checkbox.click()
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Capture baseline (no highlighting)
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
    canvas_baseline = canvas.screenshot()

    # Step 1: Enable "Highlight tracks not assigned to flows" checkbox
    not_assigned_to_flows_checkbox = page.get_by_text(
        NOT_ASSIGNED_TO_FLOWS, exact=True
    ).nth(0)
    not_assigned_to_flows_checkbox.scroll_into_view_if_needed()
    not_assigned_to_flows_checkbox.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Step 2: Navigate to Flows tab to select flows
    search_for_marker_element(page, MARKER_TAB_FLOW).first.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Get flow table reference
    flow_table = search_for_marker_element(page, MARKER_FLOW_TABLE).first
    flow_table.wait_for(state="visible")

    # Step 3: Select first flow from the flow table
    first_flow_row = flow_table.locator("table tbody tr").first
    first_flow_row.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Step 4: Verify no tracks are highlighted yet (canvas should not change)
    # Because flow highlighting has not been updated yet
    current_canvas = canvas.screenshot()
    assert (
        current_canvas == canvas_baseline
    ), "Canvas should not change before updating flow highlighting"

    # Step 5: Click "Update Flow Highlighting" button
    update_flow_button = search_for_marker_element(
        page, MARKER_UPDATE_FLOW_HIGHLIGHTING
    ).first
    update_flow_button.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Step 6: Verify canvas changed (tracks NOT assigned to first flow are highlighted)
    canvas_after_flow1 = wait_for_canvas_change(page, canvas, canvas_baseline)

    # Step 7: Select second flow from the flow table (if exists)
    second_flow_row = flow_table.locator("table tbody tr").nth(1)
    if second_flow_row.count() > 0:
        second_flow_row.click()
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
        canvas_after_flow2 = wait_for_canvas_change(page, canvas, canvas_after_flow1)
    else:
        # If only one flow exists, use the current state
        canvas_after_flow2 = canvas_after_flow1

    # Step 8: Click on "Highlight tracks not assigned to flows" again to turn it off
    not_assigned_to_flows_checkbox.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify canvas changed back (no trajectories should be shown)
    wait_for_canvas_change(page, canvas, canvas_after_flow2)
