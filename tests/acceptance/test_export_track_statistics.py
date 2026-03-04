"""Test to export track statistics and compare with reference file.

This test:
1. Loads a pre-configured project with video, tracks, sections, and flows
2. Clicks "Export track statistics ..." button
3. Verifies export dialog appears
4. Uses default values and clicks OK
5. Verifies file is created with default name
6. Compares exported file with reference file from Desktop GUI
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page  # type: ignore

from OTAnalytics.application.resources.resource_manager import (
    AnalysisKeys,
    ResourceManager,
)
from tests.acceptance.conftest import PLAYWRIGHT_VISIBLE_TIMEOUT_MS, NiceGUITestServer
from tests.utils.playwright_helpers import (
    compare_csv_files,
    export_file_via_dialog,
    load_main_page,
    open_project_otconfig,
)

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_export_track_statistics(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
    test_data_tmp_dir: Path,
) -> None:
    """Test export track statistics functionality.

    Test Steps:
    1. Load pre-configured project with tracks, sections, and flows
    2. Click "Export track statistics ..." button
    3. Verify popup appears for selecting output format
    4. Use default values
    5. Click "Ok"
    6. Verify file is created in execution folder with name "track_statistics.csv"
    7. Compare the exported file with reference file from Desktop GUI

    Expected Results:
    - Export dialog appears when button is clicked
    - File is created with correct default name
    - Exported file matches reference file content
    """
    # Setup: Load tracks with preconfigured file
    load_main_page(page, external_app)
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"

    # Load the otconfig file
    open_project_otconfig(page, resource_manager, otconfig_path)

    # Wait for tracks to load
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Click "Export track statistics ..." button
    export_button = page.get_by_text(
        resource_manager.get(AnalysisKeys.BUTTON_TEXT_EXPORT_TRACK_STATISTICS),
        exact=True,
    )
    export_button.click()

    # Handle export dialog and get output path
    output_path = export_file_via_dialog(page, test_data_tmp_dir)

    # Wait for file to be created (export operation takes several seconds)
    page.wait_for_timeout(PLAYWRIGHT_VISIBLE_TIMEOUT_MS)

    # Verify the file was created
    assert output_path.exists(), f"Track statistics file not created: {output_path}"

    # Compare with reference file
    reference_path = data_dir / "track_statistics_reference.csv"
    compare_csv_files(output_path, reference_path)
