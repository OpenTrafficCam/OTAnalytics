from pathlib import Path

import pytest
from playwright.sync_api import Page  # type: ignore

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.sections_form import (  # noqa
    MARKER_SECTION_TABLE,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
    MARKER_VISUALIZATION_LAYERS_INTERSECTING_SECTIONS,
    MARKER_VISUALIZATION_LAYERS_NOT_INTERSECTING_SECTIONS,
    MARKER_VISUALIZATION_LAYERS_START_END_POINTS_ALL,
)
from tests.acceptance.conftest import PLAYWRIGHT_SHORT_WAIT_MS, NiceGUITestServer
from tests.utils.playwright_helpers import (
    capture_and_verify_baseline,
    get_loaded_tracks_canvas_from_otconfig,
    load_main_page,
    search_for_marker_element,
)

# Ensure pytest-playwright is available; otherwise skip this module
playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_show_start_end_points_intersecting_sections(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """Acceptance (Playwright): Show start and end points
    of tracks intersecting sections.

    Test Steps:
    1. Setup: Load tracks with preconfigured sections
    2. Click "Intersecting sections" checkbox (under "Show start and end points")
    3. Select section 1
    4. Verify start (>) and end (x) points are shown on canvas
    5. Select section 2
    6. Verify start (>) and end (x) points for section 2 are shown
    7. Uncheck "Intersecting sections" checkbox
    8. Verify no start and end points are shown

    Expected Results:
    - Start and end points appear when checkbox is enabled and sections are selected
    - Canvas updates when different sections are selected
    - Start and end points disappear when checkbox is unchecked
    """
    # Setup: Load tracks with preconfigured file containing sections
    load_main_page(page, external_app)
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"
    canvas = get_loaded_tracks_canvas_from_otconfig(
        page, resource_manager, otconfig_path
    )

    # Click "Intersecting sections" checkbox (using marker)
    intersecting_sections_checkbox = page.get_by_test_id(
        MARKER_VISUALIZATION_LAYERS_INTERSECTING_SECTIONS
    )
    intersecting_sections_checkbox.scroll_into_view_if_needed()
    intersecting_sections_checkbox.click()
    page.wait_for_timeout(PLAYWRIGHT_SHORT_WAIT_MS)

    # Select section 1 (click first section in sections table)
    sections_table = search_for_marker_element(page, MARKER_SECTION_TABLE).first
    sections_table.wait_for(state="visible")
    first_section_row = sections_table.locator("tbody tr").first
    first_section_row.click()

    # Verify canvas shows start/end points for section 1
    reference_path = (
        data_dir / "test_show_start_end_points_intersecting_sections_section1.png"
    )
    capture_and_verify_baseline(canvas, reference_path, page)

    # Select section 2 (click second section in sections table)
    second_section_row = sections_table.locator("tbody tr").nth(1)
    second_section_row.click()

    # Verify canvas shows start/end points for section 2
    reference_path = (
        data_dir / "test_show_start_end_points_intersecting_sections_section2.png"
    )
    capture_and_verify_baseline(canvas, reference_path, page)

    # Uncheck "Intersecting sections" checkbox
    intersecting_sections_checkbox.click()

    # Verify canvas no longer shows start/end points
    reference_path = (
        data_dir / "test_show_start_end_points_intersecting_sections_unchecked.png"
    )
    capture_and_verify_baseline(canvas, reference_path, page)


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_show_start_end_points_not_intersecting_sections(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """Acceptance (Playwright): Show start and end points
    of tracks not intersecting sections.

    Test Steps:
    1. Setup: Load tracks with preconfigured sections
    2. Click "Not intersecting sections" checkbox
    3. Select section 1
    4. Verify start (>) and end (x) points of tracks
    NOT intersecting section 1 are shown
    5. Select section 2
    6. Verify start (>) and end (x) points of tracks
    NOT intersecting section 2 are shown
    7. Uncheck "Not intersecting sections" checkbox
    8. Verify no start and end points are shown

    Expected Results:
    - Start and end points of tracks
    NOT intersecting selected sections appear when checkbox is enabled
    - Canvas updates when different sections are selected
    - Start and end points disappear when checkbox is unchecked
    """
    # Setup: Load tracks with preconfigured file containing sections
    load_main_page(page, external_app)
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"
    canvas = get_loaded_tracks_canvas_from_otconfig(
        page, resource_manager, otconfig_path
    )

    # Click "Not intersecting sections" checkbox (using marker)
    not_intersecting_sections_checkbox = page.get_by_test_id(
        MARKER_VISUALIZATION_LAYERS_NOT_INTERSECTING_SECTIONS
    )
    not_intersecting_sections_checkbox.scroll_into_view_if_needed()
    not_intersecting_sections_checkbox.click()
    page.wait_for_timeout(PLAYWRIGHT_SHORT_WAIT_MS)

    # Select section 1 (click first section in sections table)
    sections_table = search_for_marker_element(page, MARKER_SECTION_TABLE).first
    sections_table.wait_for(state="visible")
    first_section_row = sections_table.locator("tbody tr").first
    first_section_row.click()

    # Verify canvas shows start/end points for tracks NOT intersecting section 1
    reference_path = (
        data_dir / "test_show_start_end_points_not_intersecting_sections_section1.png"
    )
    capture_and_verify_baseline(canvas, reference_path, page)

    # Select section 2 (click second section in sections table)
    second_section_row = sections_table.locator("tbody tr").nth(1)
    second_section_row.click()

    # Verify canvas shows start/end points for tracks NOT intersecting section 2
    reference_path = (
        data_dir / "test_show_start_end_points_not_intersecting_sections_section2.png"
    )
    capture_and_verify_baseline(canvas, reference_path, page)

    # Uncheck "Not intersecting sections" checkbox
    not_intersecting_sections_checkbox.click()

    # Verify canvas no longer shows start/end points
    reference_path = (
        data_dir / "test_show_start_end_points_not_intersecting_sections_unchecked.png"
    )
    capture_and_verify_baseline(canvas, reference_path, page)


@pytest.mark.skip(reason="only works in headed right now")
@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_show_all_start_end_points(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
) -> None:
    """Acceptance (Playwright): Show start and end points of all tracks.

    Test Steps:
    1. Setup: Load tracks with preconfigured sections
    2. Click "All" checkbox (under "Show start and end points")
    3. Verify start (>) and end (x) points of all tracks are shown
    4. Uncheck "All" checkbox
    5. Verify no start and end points are shown

    Expected Results:
    - Start and end points of all tracks appear when checkbox is enabled
    - Start and end points disappear when checkbox is unchecked
    """
    # Setup: Load tracks with preconfigured file containing sections
    load_main_page(page, external_app)
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"
    canvas = get_loaded_tracks_canvas_from_otconfig(
        page, resource_manager, otconfig_path
    )

    # Click "All" checkbox for start and end points (using marker)
    all_start_end_points_checkbox = page.get_by_test_id(
        MARKER_VISUALIZATION_LAYERS_START_END_POINTS_ALL
    )
    all_start_end_points_checkbox.scroll_into_view_if_needed()
    all_start_end_points_checkbox.click()

    # Verify canvas shows start/end points of all tracks
    reference_path = data_dir / "test_show_all_start_end_points_all_checked.png"
    capture_and_verify_baseline(canvas, reference_path, page)

    # Uncheck "All" checkbox
    all_start_end_points_checkbox.click()

    # Verify canvas no longer shows start/end points
    reference_path = data_dir / "test_show_all_start_end_points_unchecked.png"
    capture_and_verify_baseline(canvas, reference_path, page)
