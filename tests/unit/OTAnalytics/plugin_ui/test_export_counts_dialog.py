from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.export_formats.export_mode import OVERWRITE, ExportMode
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.export_counts_dialog import (
    MARKER_DIRECTORY,
    MARKER_FILENAME,
    MARKER_INTERVAL,
    ExportCountsDialog,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import (
    MARKER_APPLY,
    MARKER_CANCEL,
)

# Constants for testing
TEST_START = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
TEST_END = datetime(2023, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
TEST_DEFAULT_FORMAT = "CSV"
TEST_MODES = ExportMode.values()
TEST_EXPORT_FORMATS = {"CSV": "csv", "Excel": "xlsx"}
TEST_INTERVAL = 15
TEST_OUTPUT_FILE = "/test/directory/test_file.csv"
TEST_EXCEL_OUTPUT_FILE = "/test/directory/test_file.xlsx"
ENDPOINT_NAME = "/test-export-counts-dialog"


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
        viewmodel: Mock,
    ) -> None:
        """Test that the dialog builds up correctly and all elements are visible."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            export_counts_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Check that all elements are visible
        await user.should_see(marker=MARKER_FILENAME)
        await user.should_see(marker=MARKER_DIRECTORY)
        await user.should_see(marker=MARKER_INTERVAL)
        await user.should_see(marker=MARKER_APPLY)
        await user.should_see(marker=MARKER_CANCEL)

    @pytest.mark.asyncio
    async def test_get_specification(
        self,
        user: User,
        export_counts_dialog: ExportCountsDialog,
        resource_manager: ResourceManager,
    ) -> None:
        """Test that get_specification returns the correct specification."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            export_counts_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        user.find(MARKER_DIRECTORY).type(str(Path(TEST_OUTPUT_FILE).parent))
        user.find(MARKER_FILENAME).type(Path(TEST_OUTPUT_FILE).name)
        user.find(marker=MARKER_APPLY).click()

        # Patch the get_file_path method to return the expected path
        with patch.object(
            export_counts_dialog, "get_file_path", return_value=Path(TEST_OUTPUT_FILE)
        ):
            specification = export_counts_dialog.get_specification()

            assert specification.start == TEST_START
            assert specification.end == TEST_END
            assert specification.output_format == TEST_DEFAULT_FORMAT
            assert Path(specification.output_file) == Path(TEST_OUTPUT_FILE)
            assert specification.export_mode == OVERWRITE
            assert specification.interval_in_minutes == TEST_INTERVAL

    @pytest.mark.asyncio
    async def test_different_export_format(
        self,
        user: User,
        resource_manager: ResourceManager,
        viewmodel: Mock,
    ) -> None:
        """Test that different export formats work correctly."""
        # Create a dialog with Excel as the default format
        export_counts_dialog = ExportCountsDialog(
            resource_manager=resource_manager,
            viewmodel=viewmodel,
            start=TEST_START,
            end=TEST_END,
            default_format="Excel",
            modes=TEST_MODES,
            export_formats=TEST_EXPORT_FORMATS,
        )

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            export_counts_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        user.find(MARKER_DIRECTORY).type(str(Path(TEST_EXCEL_OUTPUT_FILE).parent))
        user.find(MARKER_FILENAME).type(Path(TEST_EXCEL_OUTPUT_FILE).name)
        user.find(marker=MARKER_APPLY).click()

        # Patch the get_file_path method to return the expected path
        with patch.object(
            export_counts_dialog,
            "get_file_path",
            return_value=Path(TEST_EXCEL_OUTPUT_FILE),
        ):
            specification = export_counts_dialog.get_specification()

            assert specification.output_format == "Excel"
            assert Path(specification.output_file) == Path(TEST_EXCEL_OUTPUT_FILE)

    @pytest.mark.asyncio
    async def test_validation_error_empty_filename(
        self,
        user: User,
        export_counts_dialog: ExportCountsDialog,
    ) -> None:
        """Test that validation errors are handled correctly for empty filename."""

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            export_counts_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Set directory but leave filename empty
        user.find(MARKER_DIRECTORY).type(str(Path(TEST_OUTPUT_FILE).parent))
        user.find(MARKER_FILENAME).clear()
        user.find(marker=MARKER_APPLY).click()

        # Verify that get_specification raises a ValueError
        with pytest.raises(ValueError, match="No output file selected"):
            export_counts_dialog.get_specification()

    @pytest.mark.asyncio
    async def test_validation_error_missing_dates(
        self,
        user: User,
        resource_manager: ResourceManager,
        viewmodel: Mock,
    ) -> None:
        """Test that validation errors are handled correctly for missing dates."""
        # Create a dialog with no start and end dates
        export_counts_dialog = ExportCountsDialog(
            resource_manager=resource_manager,
            viewmodel=viewmodel,
            start=None,
            end=None,
            default_format=TEST_DEFAULT_FORMAT,
            modes=TEST_MODES,
            export_formats=TEST_EXPORT_FORMATS,
        )

        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            export_counts_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Set directory and filename but leave dates empty
        user.find(MARKER_DIRECTORY).type(str(Path(TEST_OUTPUT_FILE).parent))
        user.find(MARKER_FILENAME).type(Path(TEST_OUTPUT_FILE).name)
        user.find(marker=MARKER_APPLY).click()

        # Verify that get_specification raises a ValueError
        with pytest.raises(ValueError, match="Start and end times must be specified"):
            export_counts_dialog.get_specification()
