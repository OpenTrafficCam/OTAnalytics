"""Test to export road user assignments and compare with reference file.

This test:
1. Loads a pre-configured project with video, tracks, sections, and flows
2. Clicks "Export road user assignments ..." button
3. Verifies export dialog appears
4. Uses default values and clicks OK
5. Verifies file is created with default name
6. Compares exported file with reference file from Desktop GUI
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page  # type: ignore

from OTAnalytics.application.resources.resource_manager import ResourceManager
from tests.acceptance.conftest import NiceGUITestServer
from tests.utils.playwright_helpers import (
    compare_csv_files,
    export_road_user_assignments,
)

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_export_road_user_assignments(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
    test_data_tmp_dir: Path,
) -> None:
    """Test export road user assignments functionality.

    Test Steps:
    1. Load pre-configured project with tracks, sections, and flows
    2. Click "Export road user assignments ..." button
    3. Verify popup appears for selecting output format
    4. Use default values
    5. Click "Ok"
    6. Verify file is created in execution folder with name "road_user_assignments.csv"
    7. Compare the exported file with reference file from Desktop GUI

    Expected Results:
    - Export dialog appears when button is clicked
    - File is created with correct default name
    - Exported file matches reference file content
    """
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"

    # Export road user assignments
    output_path = export_road_user_assignments(
        page, external_app, resource_manager, test_data_tmp_dir, otconfig_path
    )

    # Compare with reference file
    reference_path = (
        data_dir
        / "Testvideo_Cars-Cyclist_FR20_2020-01-01_00-00-00.road_user_assignments.csv"
    )
    compare_csv_files(output_path, reference_path)
