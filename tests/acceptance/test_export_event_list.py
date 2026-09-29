"""Test to export event list and compare with reference file.

This test:
1. Loads a pre-configured project with video, tracks, sections, and flows
2. Clicks "Export eventlist ..." button
3. Verifies export dialog appears
4. Selects "CSV (OpenTrafficCam)" format (default)
5. Uses default values and clicks OK
6. Verifies file is created with default name
7. Compares exported file with reference file from Desktop GUI
"""

from pathlib import Path

import pytest
from playwright.sync_api import Page  # type: ignore

from OTAnalytics.application.resources.resource_manager import ResourceManager
from tests.acceptance.conftest import NiceGUITestServer
from tests.utils.playwright_helpers import compare_csv_files, export_event_list

playwright = pytest.importorskip(
    "playwright.sync_api", reason="pytest-playwright is required for this test"
)


@pytest.mark.timeout(300)
@pytest.mark.playwright
@pytest.mark.usefixtures("external_app")
def test_export_event_list(
    page: Page,
    external_app: NiceGUITestServer,
    resource_manager: ResourceManager,
    test_data_tmp_dir: Path,
) -> None:
    """Test export event list functionality.

    Test Steps:
    1. Load pre-configured project with tracks, sections, and flows
    2. Click "Export eventlist ..." button
    3. Verify popup appears for selecting output format
    4. Select "CSV (OpenTrafficCam)" (default)
    5. Use default file name (name of the project or start date)
    6. Click "Ok"
    7. Verify file is created in execution folder with default name
    8. Compare the exported file with reference file from Desktop GUI

    Expected Results:
    - Export dialog appears when button is clicked
    - File is created with correct default name
    - Exported file matches reference file content
    """
    data_dir = Path(__file__).parents[1] / "data"
    otconfig_path = data_dir / "sections_created_test_file.otconfig"

    # Export event list
    output_path = export_event_list(
        page, external_app, resource_manager, test_data_tmp_dir, otconfig_path
    )

    # Compare with reference file
    reference_path = data_dir / "events_reference.csv"
    compare_csv_files(output_path, reference_path)
