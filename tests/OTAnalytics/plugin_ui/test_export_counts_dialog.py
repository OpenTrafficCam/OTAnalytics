from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.export_formats.export_mode import OVERWRITE, ExportMode
from OTAnalytics.application.resources.resource_manager import (
    GeneralKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.export_counts_dialog import (
    MARKER_DIRECTORY,
    MARKER_FILENAME,
    ExportCountsDialog,
)

# Constants for testing
TEST_START = datetime(2023, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
TEST_END = datetime(2023, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
TEST_DEFAULT_FORMAT = "CSV"
TEST_MODES = ExportMode.values()
TEST_EXPORT_FORMATS = {"CSV": "csv", "Excel": "xlsx"}
TEST_INTERVAL = 15
TEST_OUTPUT_FILE = "/test/directory/test_file.csv"
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
        @ui.page(ENDPOINT_NAME)
        def page() -> None:
            export_counts_dialog.build().open()

        await user.open(ENDPOINT_NAME)

        # Check that all elements are visible
        await user.should_see(marker=MARKER_FILENAME)  # From resource_manager.get()

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
        user.find(resource_manager.get(GeneralKeys.LABEL_APPLY)).click()

        specification = export_counts_dialog.get_specification()

        assert specification.start == TEST_START
        assert specification.end == TEST_END
        assert specification.output_format == TEST_DEFAULT_FORMAT
        assert specification.output_file == TEST_OUTPUT_FILE
        assert specification.export_mode == OVERWRITE
