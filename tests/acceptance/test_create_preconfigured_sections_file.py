"""Test to create a pre-configured .otconfig file with video, tracks, and sections.

This test creates a configuration file that can be used by other tests to skip
the setup steps of adding videos, tracks, and creating sections.
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page  # type: ignore  # noqa: E402

from OTAnalytics.application.resources.resource_manager import (
    ResourceManager,
    TrackFormKeys,
)
from tests.acceptance.conftest import ACCEPTANCE_TEST_PYTEST_TIMEOUT, NiceGUITestServer
from tests.utils.playwright_helpers import (
    add_track_via_picker,
    add_video_via_picker,
    create_flow,
    create_section,
    navigate_and_prepare,
    save_project_as,
    search_for_marker_element,
    wait_for_flow_present,
)

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


class TestCreatePreconfiguredSectionsFile:

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
        video_file = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.mp4"
        track_file = data_dir / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.ottrk"

        assert video_file.exists(), f"Test video missing: {video_file}"
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
