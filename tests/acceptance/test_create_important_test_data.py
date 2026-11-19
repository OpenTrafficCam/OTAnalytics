"""Test to create important test data files: pre-configured
.otconfig file and reference screenshots.

This test creates:
1. A pre-configured .otconfig file with video, tracks, and sections
2. Reference screenshots for all visualization layer states

These test data files can be used by other tests to skip setup steps.
"""

import json
import shutil
from pathlib import Path

import pytest
from playwright.sync_api import Locator, Page, expect  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.container import (
    MARKER_TRACK_TAB,
    MARKER_VIDEO_TAB,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.canvas_and_files_form.canvas_form import (
    MARKER_INTERACTIVE_IMAGE,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.container import (
    MARKER_TAB_FLOW,
    MARKER_TAB_SECTION,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.sections_and_flow_form.flow_form import (
    MARKER_FLOW_TABLE,
)
from OTAnalytics.plugin_ui.nicegui_gui.pages.visualization_layers_form.layers_form import (  # noqa
    MARKER_VISUALIZATION_LAYERS_ALL,
)
from OTAnalytics.plugin_ui.visualization.visualization import (
    ALL,
    ASSIGNED_TO_FLOWS,
    INTERSECTING_SECTIONS,
    NOT_ASSIGNED_TO_FLOWS,
    NOT_INTERSECTING_SECTIONS,
)
from tests.acceptance.conftest import (
    ACCEPTANCE_TEST_PYTEST_TIMEOUT,
    ACCEPTANCE_TEST_TRACK_FILES,
    ACCEPTANCE_TEST_VIDEO_FILE,
    PLAYWRIGHT_VISIBLE_TIMEOUT_MS,
    SECTIONS,
    TRACK_LOADING_TIMEOUT_MS,
    NiceGUITestServer,
)
from tests.utils.playwright_helpers import (
    add_track_via_picker,
    add_video_via_picker,
    click_table_cell_with_text,
    click_update_offset_button,
    create_flow,
    create_section,
    enable_all_tracks_layer,
    export_track_statistics,
    get_loaded_tracks_canvas_from_otconfig,
    get_test_files_from_data_dir,
    load_main_page,
    navigate_and_prepare,
    save_canvas,
    save_project_as,
    search_for_marker_element,
    setup_tracks_display,
    toggle_and_screenshot,
    update_flow_highlighting,
    wait_for_canvas_change,
    wait_for_flow_present,
    wait_for_names_present,
)

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)

# Screenshot file prefix and occurrence of the layer checkbox text:
# nth=0 is the "Show tracks" group, nth=1 the "Show start and end points" group
TRACKS_GROUP = ("highlight_tracks", 0)
START_END_GROUP = ("start_end", 1)

VISUALIZATION_LAYER_SCREENSHOTS = [
    (TRACKS_GROUP, INTERSECTING_SECTIONS, "intersecting_sections"),
    (TRACKS_GROUP, NOT_INTERSECTING_SECTIONS, "not_intersecting_sections"),
    (TRACKS_GROUP, ASSIGNED_TO_FLOWS, "assigned_to_flows"),
    (TRACKS_GROUP, NOT_ASSIGNED_TO_FLOWS, "not_assigned_to_flows"),
    (START_END_GROUP, INTERSECTING_SECTIONS, "intersecting_sections"),
    (START_END_GROUP, NOT_INTERSECTING_SECTIONS, "not_intersecting_sections"),
    (START_END_GROUP, ALL, "all"),
    (START_END_GROUP, ASSIGNED_TO_FLOWS, "assigned_to_flows"),
    (START_END_GROUP, NOT_ASSIGNED_TO_FLOWS, "not_assigned_to_flows"),
]


def _select_flow(page: Page, flow_name: str) -> None:
    search_for_marker_element(page, MARKER_TAB_FLOW).first.click()
    search_for_marker_element(page, MARKER_FLOW_TABLE).locator(
        "tbody tr", has_text=flow_name
    ).first.click()
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)


def _disable_all_tracks_layer(page: Page, canvas: Locator) -> None:
    image = canvas.locator(":scope > img")
    all_tracks = image.get_attribute("src") or ""
    all_tracks_checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
    # The checkbox only changes once the app confirmed it, so no uncheck()
    all_tracks_checkbox.click()
    # The app may still be busy plotting the previous step
    expect(all_tracks_checkbox).not_to_be_checked(timeout=TRACK_LOADING_TIMEOUT_MS)
    expect(image).not_to_have_attribute(
        "src", all_tracks, timeout=TRACK_LOADING_TIMEOUT_MS
    )
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
    # Pending updates of the app may check it again
    expect(all_tracks_checkbox).not_to_be_checked()


# @pytest.mark.skip
class TestCreateImportantTestData:
    @pytest.mark.skip
    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_create_preconfigured_sections_file(
        self,
        page: Page,
        external_app: NiceGUITestServer,
        resource_manager: ResourceManager,
        test_data_tmp_dir: Path,
    ) -> None:
        """Create a pre-configured .otconfig
        file with video, tracks, sections, and flows.

        This test goes through all the setup steps:
        - Navigate to the main page and fill project information
        - Add a test video
        - Add track files
        - Create the SECTIONS
        - Create the flows between them in both directions
        - Save the configuration as 'sections_created_test_file.otconfig'

        The resulting file can be used by other tests to skip these setup steps.
        """
        # Navigate and prepare the page with project information
        navigate_and_prepare(
            page,
            external_app,
            resource_manager,
            name="Preconfigured Test Project",
            date_value="2020-01-01",
            time_value="00:00:00",
        )

        # Setup paths to test data
        data_dir = Path(__file__).parents[1] / "data"
        video_file = data_dir / ACCEPTANCE_TEST_VIDEO_FILE
        track_files = [data_dir / filename for filename in ACCEPTANCE_TEST_TRACK_FILES]

        assert video_file.exists(), f"Test video missing: {video_file}"
        for track_file in track_files:
            assert track_file.exists(), f"Test track file missing: {track_file}"

        # Add video
        search_for_marker_element(page, MARKER_VIDEO_TAB).first.click()

        add_video_via_picker(page, resource_manager, video_file)

        # Wait for video to be added and select it
        wait_for_names_present(page, [video_file.name])
        click_table_cell_with_text(page, video_file.name)

        # Add tracks
        search_for_marker_element(page, MARKER_TRACK_TAB).first.click()
        for track_file in track_files:
            add_track_via_picker(page, resource_manager, track_file)

        # Switch to Sections tab
        search_for_marker_element(page, MARKER_TAB_SECTION).first.click()

        # Clicks are in pixels of the displayed canvas, not of the image
        image = search_for_marker_element(page, MARKER_INTERACTIVE_IMAGE).locator("img")
        scale = image.evaluate("image => image.clientWidth / image.naturalWidth")
        for name, points in SECTIONS.items():
            positions = [(x * scale, y * scale) for x, y in points]
            create_section(page, resource_manager, name, positions=positions)

        search_for_marker_element(page, MARKER_TAB_FLOW).first.click()
        first, second = SECTIONS
        flows = {
            f"{first} --> {second}": (first, second),
            f"{second} --> {first}": (second, first),
        }
        for flow_name, (start, end) in flows.items():
            create_flow(
                page,
                resource_manager,
                flow_name,
                list(SECTIONS).index(start),
                list(SECTIONS).index(end),
            )
            wait_for_flow_present(page, flow_name)

        output_path = test_data_tmp_dir / "sections_created_test_file.otconfig"
        save_project_as(page, resource_manager, output_path)
        assert output_path.exists(), f"Configuration file not created: {output_path}"

        # The flow dialog selects sections by position, so check the directions
        saved = json.loads(output_path.read_text())
        names = {section["id"]: section["name"] for section in saved["sections"]}
        assert {
            flow["name"]: (names[flow["start"]], names[flow["end"]])
            for flow in saved["flows"]
        } == flows

        # Also copy to the main test data directory for reuse
        permanent_path = data_dir / "sections_created_test_file.otconfig"
        shutil.copy(output_path, permanent_path)

        print(f"\nPre-configured file created at: {permanent_path}")

    @pytest.mark.skip(reason="only works in headed right now")
    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_generate_canvas_screenshots(
        self,
        external_app: NiceGUITestServer,
        page: Page,
        resource_manager: ResourceManager,
        acceptance_test_data_folder: Path,
    ) -> None:
        """Generate reference screenshots for all visualization layer states."""
        # Setup: Load tracks with preconfigured file
        load_main_page(page, external_app)
        data_dir = Path(__file__).parents[1] / "data"
        otconfig_path = data_dir / "sections_created_test_file.otconfig"
        canvas = get_loaded_tracks_canvas_from_otconfig(
            page, resource_manager, otconfig_path
        )

        # Show all tracks (already enabled), as the tests see them after loading
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
        save_canvas(canvas, acceptance_test_data_folder / "all_tracks.png")

        # Sections and flows are already loaded from the preconfigured file.
        # The flow layers only show the selected flows.
        update_flow_highlighting(page)
        first, second = SECTIONS
        _select_flow(page, f"{first} --> {second}")

        # Update with section offset, while all tracks show the offset
        # This button may be disabled if preconditions aren't met
        click_update_offset_button(page, canvas, acceptance_test_data_folder)

        # Turn off "All" tracks, so each screenshot shows only its own layer
        _disable_all_tracks_layer(page, canvas)
        for (prefix, nth), layer, suffix in VISUALIZATION_LAYER_SCREENSHOTS:
            toggle_and_screenshot(
                page,
                canvas,
                layer,
                acceptance_test_data_folder,
                f"{prefix}_{suffix}",
                nth=nth,
            )

    @pytest.mark.skip(reason="only works in headed right now")
    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_generate_added_tracks_screenshot(
        self,
        external_app: NiceGUITestServer,
        page: Page,
        resource_manager: ResourceManager,
        acceptance_test_data_folder: Path,
    ) -> None:
        """Generate the reference screenshot of tracks added via the file picker.

        Unlike the preconfigured file, this shows all track files and no sections.
        """
        load_main_page(page, external_app)
        data_dir = Path(__file__).parents[1] / "data"
        video_file, track_files = get_test_files_from_data_dir(data_dir)
        canvas = setup_tracks_display(
            page, resource_manager, video_file, track_files, enable_tracks_layer=False
        )
        canvas_before_tracks = canvas.screenshot()

        enable_all_tracks_layer(page)
        wait_for_canvas_change(
            page, canvas, canvas_before_tracks, timeout=TRACK_LOADING_TIMEOUT_MS / 1000
        )

        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
        save_canvas(canvas, acceptance_test_data_folder / "added_tracks.png")

    @pytest.mark.timeout(ACCEPTANCE_TEST_PYTEST_TIMEOUT)
    @pytest.mark.playwright
    @pytest.mark.usefixtures("external_app")
    def test_generate_track_statistics_reference_file(
        self,
        external_app: NiceGUITestServer,
        page: Page,
        resource_manager: ResourceManager,
        test_data_tmp_dir: Path,
    ) -> None:
        """Generate reference track_statistics.csv file using Desktop GUI.

        This test:
        - Loads a pre-configured project with video, tracks, sections, and flows
        - Clicks "Export track statistics ..."
        - Uses default values in the export dialog
        - Saves the file
        - Copies it to the test data directory as reference

        The resulting file can be used by other tests to compare exported output.
        """
        data_dir = Path(__file__).parents[1] / "data"
        otconfig_path = data_dir / "sections_created_test_file.otconfig"

        # Export track statistics
        output_path = export_track_statistics(
            page, external_app, resource_manager, test_data_tmp_dir, otconfig_path
        )

        # Copy to the main test data directory for reuse
        permanent_path = data_dir / "track_statistics_reference.csv"
        shutil.copy(output_path, permanent_path)
