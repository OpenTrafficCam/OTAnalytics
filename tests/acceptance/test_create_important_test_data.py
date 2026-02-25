"""Test to create important test data files: pre-configured
.otconfig file and reference screenshots.

This test creates:
1. A pre-configured .otconfig file with video, tracks, and sections
2. Reference screenshots for all visualization layer states

These test data files can be used by other tests to skip setup steps.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    TrackFormKeys,
    VisualizationLayersKeys,
    VisualizationOffsetSliderKeys,
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
    NiceGUITestServer,
)
from tests.utils.playwright_helpers import (
    add_track_via_picker,
    add_video_via_picker,
    create_flow,
    create_section,
    get_loaded_tracks_canvas_from_otconfig,
    navigate_and_prepare,
    navigate_to_main_page_with_url,
    save_project_as,
    search_for_marker_element,
    wait_for_flow_present,
)

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


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
        - Create two sections with different coordinates
        - Create a flow between the sections
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
        try:
            from OTAnalytics.plugin_ui.nicegui_gui.pages.add_track_form.container import (  # noqa
                MARKER_VIDEO_TAB,
            )

            search_for_marker_element(page, MARKER_VIDEO_TAB).first.click()
        except Exception:
            page.get_by_text(
                resource_manager.get(TrackFormKeys.TAB_VIDEO), exact=True
            ).click()

        add_video_via_picker(page, resource_manager, video_file)

        # Wait for video to be added and select it
        from tests.utils.playwright_helpers import (
            click_table_cell_with_text,
            wait_for_names_present,
        )

        wait_for_names_present(page, [video_file.name])
        click_table_cell_with_text(page, video_file.name)

        # Add tracks
        page.get_by_text(
            resource_manager.get(TrackFormKeys.TAB_TRACK), exact=True
        ).click()
        for track_file in track_files:
            add_track_via_picker(page, resource_manager, track_file)

        # Switch to Sections tab
        from OTAnalytics.application.resources.resource_manager import (
            FlowAndSectionKeys,
        )

        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_SECTION), exact=True
        ).click()

        # Create two sections with different names and coordinates
        section_names = ["North-Section", "South-Section"]
        section_coords = [
            [(20, 20), (140, 60)],  # First section coordinates
            [(220, 80), (340, 140)],  # Second section coordinates
        ]

        for name, coords in zip(section_names, section_coords):
            create_section(page, resource_manager, name, positions=coords)

        # Switch to Flows tab and create flows
        page.get_by_text(
            resource_manager.get(FlowAndSectionKeys.TAB_FLOW), exact=True
        ).click()

        # Create a flow between the two sections
        flow_name = "Test-Flow"
        create_flow(
            page,
            resource_manager,
            flow_name,
            start_section_index=0,
            end_section_index=1,
        )
        wait_for_flow_present(page, flow_name)

        # Save the configuration file
        output_path = test_data_tmp_dir / "sections_created_test_file.otconfig"
        save_project_as(page, resource_manager, output_path)

        # Verify the file was created
        assert output_path.exists(), f"Configuration file not created: {output_path}"

        # Also copy to the main test data directory for reuse
        permanent_path = data_dir / "sections_created_test_file.otconfig"
        import shutil

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
        base_url = getattr(external_app, "base_url", "http://127.0.0.1:8080")
        navigate_to_main_page_with_url(page, base_url)
        data_dir = Path(__file__).parents[1] / "data"
        otconfig_path = data_dir / "sections_created_test_file.otconfig"
        canvas = get_loaded_tracks_canvas_from_otconfig(
            page, resource_manager, otconfig_path
        )

        # Helper function to toggle a checkbox and take screenshot
        def toggle_and_screenshot(
            checkbox_text: str, filename_base: str, nth: int = 0
        ) -> None:
            """Toggle a checkbox on, take screenshot, then toggle off.

            Args:
                checkbox_text: Text of the checkbox to find
                filename_base: Base name for screenshot files
                nth: Which occurrence to use if multiple checkboxes have same text
            """
            checkbox = page.get_by_text(checkbox_text, exact=True).nth(nth)
            checkbox.scroll_into_view_if_needed()

            # Toggle on and screenshot
            if not checkbox.is_checked():
                checkbox.click()
            page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
            canvas.screenshot(path=acceptance_test_data_folder / f"{filename_base}.png")

            # Toggle off (no screenshot)
            checkbox.click()
            page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

        # 1. Show all tracks (already enabled, just take screenshot)
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
        canvas.screenshot(path=acceptance_test_data_folder / "all_tracks.png")

        # Sections and flows are already loaded from the preconfigured file
        # Just update flow highlighting
        page.get_by_text(
            resource_manager.get(
                VisualizationLayersKeys.BUTTON_UPDATE_FLOW_HIGHLIGHTING
            ),
            exact=True,
        ).click()
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

        # Turn off "Show all tracks" to prepare for next screenshots
        all_tracks_checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
        all_tracks_checkbox.click()
        page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

        # 2. Show offset ändern und zurücksetzen (Update with section offset button)
        # This button may be disabled if preconditions
        # aren't met, so skip if not enabled
        offset_button = page.get_by_text(
            resource_manager.get(VisualizationOffsetSliderKeys.BUTTON_UPDATE_OFFSET),
            exact=True,
        )
        if offset_button.count() > 0:
            offset_button.scroll_into_view_if_needed()
            canvas.screenshot(path=acceptance_test_data_folder / "offset_before.png")
            # Only click if enabled
            if not offset_button.is_disabled():
                offset_button.click()
                page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)
                canvas.screenshot(path=acceptance_test_data_folder / "offset_after.png")

        # 3-11. Toggle all visualization layers and take screenshots
        # Deselect "Show all tracks" before testing individual highlight options
        all_tracks_checkbox = page.get_by_test_id(MARKER_VISUALIZATION_LAYERS_ALL)
        if all_tracks_checkbox.is_checked():
            all_tracks_checkbox.click()
            page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

        # Show tracks group (nth=0 means first occurrence in "Show tracks" section)
        toggle_and_screenshot(
            INTERSECTING_SECTIONS, "highlight_tracks_intersecting_sections", nth=0
        )
        toggle_and_screenshot(
            NOT_INTERSECTING_SECTIONS,
            "highlight_tracks_not_intersecting_sections",
            nth=0,
        )
        toggle_and_screenshot(
            ASSIGNED_TO_FLOWS, "highlight_tracks_assigned_to_flows", nth=0
        )
        toggle_and_screenshot(
            NOT_ASSIGNED_TO_FLOWS, "highlight_tracks_not_assigned_to_flows", nth=0
        )

        # Show start and end points group
        # (nth=1 means second occurrence in "Show start and end points" section)
        toggle_and_screenshot(
            INTERSECTING_SECTIONS, "start_end_intersecting_sections", nth=1
        )
        toggle_and_screenshot(
            NOT_INTERSECTING_SECTIONS, "start_end_not_intersecting_sections", nth=1
        )
        toggle_and_screenshot(ALL, "start_end_all", nth=1)
        toggle_and_screenshot(ASSIGNED_TO_FLOWS, "start_end_assigned_to_flows", nth=1)
        toggle_and_screenshot(
            NOT_ASSIGNED_TO_FLOWS, "start_end_not_assigned_to_flows", nth=1
        )
