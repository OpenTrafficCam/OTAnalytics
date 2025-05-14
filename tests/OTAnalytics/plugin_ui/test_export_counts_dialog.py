from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.export_formats.export_mode import OVERWRITE, ExportMode
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.export_counts_dialog import (
    ExportCountsDialog,
)

# Constants for testing
TEST_START = datetime(2023, 1, 1, 0, 0, 0)
TEST_END = datetime(2023, 1, 2, 0, 0, 0)
TEST_DEFAULT_FORMAT = "CSV"
TEST_MODES = ExportMode.values()
TEST_EXPORT_FORMATS = {"CSV": "csv", "Excel": "xlsx"}
TEST_INTERVAL = 15
TEST_OUTPUT_FILE = "/test/directory/test_file.csv"
ENDPOINT_NAME = "/test-export-counts-dialog"


@pytest.fixture
def resource_manager() -> Mock:
    resource_manager = MagicMock(spec=ResourceManager)
    resource_manager.get.return_value = "Test Label"
    return resource_manager


@pytest.fixture
def viewmodel() -> Mock:
    viewmodel = MagicMock(spec=ViewModel)
    viewmodel.get_save_path_suggestion.return_value = Path(TEST_OUTPUT_FILE)
    return viewmodel


@pytest.fixture
def export_counts_dialog(resource_manager: Mock, viewmodel: Mock) -> ExportCountsDialog:
    return ExportCountsDialog(
        resource_manager=resource_manager,
        viewmodel=viewmodel,
        start=TEST_START,
        end=TEST_END,
        default_format=TEST_DEFAULT_FORMAT,
        modes=TEST_MODES,
        export_formats=TEST_EXPORT_FORMATS,
    )


class TestExportCountsDialog:
    @pytest.mark.asyncio
    async def test_dialog_build_up(
        self,
        user: User,
        export_counts_dialog: ExportCountsDialog,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that the dialog builds correctly and displays all elements."""

        @ui.page(ENDPOINT_NAME)
        async def page() -> None:
            await export_counts_dialog.build()

        await user.open(ENDPOINT_NAME)

        # Check that all elements are visible
        await user.should_see("Test Label")  # From resource_manager.get()

    @pytest.mark.asyncio
    async def test_get_specification(
        self, user: User, export_counts_dialog: ExportCountsDialog
    ) -> None:
        """Test that get_specification returns the correct specification."""

        @ui.page(ENDPOINT_NAME)
        async def page() -> None:
            await export_counts_dialog.build()

        await user.open(ENDPOINT_NAME)

        # Set the directory and filename fields
        export_counts_dialog._directory_field.set_value(
            str(Path(TEST_OUTPUT_FILE).parent)
        )
        export_counts_dialog._filename_field.set_value(Path(TEST_OUTPUT_FILE).name)

        # Set the interval
        export_counts_dialog._interval.set_value(TEST_INTERVAL)

        # Get the specification
        specification = export_counts_dialog.get_specification()

        # Verify that the specification is correct
        assert specification.start == TEST_START
        assert specification.end == TEST_END
        assert specification.interval_in_minutes == TEST_INTERVAL
        assert specification.output_format == TEST_DEFAULT_FORMAT
        assert specification.output_file == TEST_OUTPUT_FILE
        assert specification.export_mode == OVERWRITE
