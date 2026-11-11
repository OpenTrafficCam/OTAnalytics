from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
from nicegui import ui
from nicegui.testing import User

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
)
from OTAnalytics.application.config import (
    CONTEXT_FILE_TYPE_COUNTS,
    DEFAULT_COUNT_INTERVAL_TIME_UNIT,
)
from OTAnalytics.application.export_formats.export_mode import OVERWRITE, ExportMode
from OTAnalytics.application.resources.resource_manager import ResourceManager
from OTAnalytics.application.state import CurrentExportConfigState
from OTAnalytics.application.use_cases.static_analysis_config import (
    GetCountingEventOfCurrentAnalysisConfig,
    GetCountIntervalsOfCurrentAnalysisConfig,
    GetSaveNameOfCurrentAnalysisConfig,
    GetSaveSuffixOfCurrentAnalysisConfig,
)
from OTAnalytics.application.use_cases.suggest_save_path import SavePathSuggestion
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.export_counts_dialog import (
    MARKER_DIRECTORY,
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
TEST_SECOND_INTERVAL = 60
TEST_FILE_DIR = "test/directory"
TEST_FILE_STEM = "test_file"
TEST_SAVE_NAME = "my_counts"
TEST_SAVE_SUFFIX = "my_suffix"
TEST_OUTPUT_FILE = f"/{TEST_FILE_DIR}/{TEST_FILE_STEM}.csv"
TEST_EXCEL_OUTPUT_FILE = f"/{TEST_FILE_DIR}/{TEST_FILE_STEM}.xlsx"
TEST_CONTEXT_FILE_TYPE = (
    f"{CONTEXT_FILE_TYPE_COUNTS}_{TEST_INTERVAL}{DEFAULT_COUNT_INTERVAL_TIME_UNIT}"
)
SAVE_PATH_SUGGESTION = SavePathSuggestion(
    save_directory=Path(TEST_FILE_DIR),
    file_stem=TEST_FILE_STEM,
    context_file_type=TEST_CONTEXT_FILE_TYPE,
    file_type=".csv",
)
ENDPOINT_NAME = "/test-export-counts-dialog"


@pytest.fixture
def viewmodel() -> Mock:
    viewmodel = MagicMock(spec=ViewModel)
    viewmodel.get_save_path_suggestion.return_value = SAVE_PATH_SUGGESTION
    return viewmodel


@pytest.fixture
def export_config_state() -> CurrentExportConfigState:
    state = CurrentExportConfigState()
    state.count_intervals = {TEST_INTERVAL}
    state.counting_event = CountingEvent.START
    state.save_name = ""
    state.save_suffix = ""
    return state


def build_dialog(
    resource_manager: ResourceManager,
    viewmodel: Mock,
    export_config_state: CurrentExportConfigState,
    start: datetime | None = TEST_START,
    end: datetime | None = TEST_END,
    default_format: str = TEST_DEFAULT_FORMAT,
) -> ExportCountsDialog:
    return ExportCountsDialog(
        resource_manager=resource_manager,
        viewmodel=viewmodel,
        start=start,
        end=end,
        default_format=default_format,
        modes=TEST_MODES,
        export_formats=TEST_EXPORT_FORMATS,
        get_count_intervals=GetCountIntervalsOfCurrentAnalysisConfig(
            export_config_state
        ),
        get_counting_event=GetCountingEventOfCurrentAnalysisConfig(export_config_state),
        get_save_name=GetSaveNameOfCurrentAnalysisConfig(export_config_state),
        get_save_suffix=GetSaveSuffixOfCurrentAnalysisConfig(export_config_state),
    )


@pytest.fixture
def export_counts_dialog(
    resource_manager: ResourceManager,
    viewmodel: Mock,
    export_config_state: CurrentExportConfigState,
) -> ExportCountsDialog:
    return build_dialog(resource_manager, viewmodel, export_config_state)


def open_dialog(dialog: ExportCountsDialog) -> None:
    @ui.page(ENDPOINT_NAME)
    def page() -> None:
        dialog.build().open()


class TestExportCountsDialog:
    @pytest.mark.asyncio
    async def test_dialog_build_up(
        self,
        user: User,
        export_counts_dialog: ExportCountsDialog,
    ) -> None:
        """Test that the dialog builds up correctly and all elements are visible."""
        open_dialog(export_counts_dialog)

        await user.open(ENDPOINT_NAME)

        await user.should_see(marker=MARKER_DIRECTORY)
        await user.should_see(marker=MARKER_APPLY)
        await user.should_see(marker=MARKER_CANCEL)

    @pytest.mark.asyncio
    async def test_single_interval_is_not_offered(
        self,
        user: User,
        export_counts_dialog: ExportCountsDialog,
    ) -> None:
        open_dialog(export_counts_dialog)

        await user.open(ENDPOINT_NAME)

        await user.should_not_see(marker=MARKER_INTERVAL)

    @pytest.mark.asyncio
    async def test_several_intervals_are_offered(
        self,
        user: User,
        resource_manager: ResourceManager,
        viewmodel: Mock,
        export_config_state: CurrentExportConfigState,
    ) -> None:
        export_config_state.count_intervals = {TEST_INTERVAL, TEST_SECOND_INTERVAL}
        dialog = build_dialog(resource_manager, viewmodel, export_config_state)
        open_dialog(dialog)

        await user.open(ENDPOINT_NAME)

        await user.should_see(marker=MARKER_INTERVAL)
        assert dialog.get_specification().interval_in_minutes == TEST_INTERVAL

    @pytest.mark.asyncio
    async def test_selected_interval_is_used(
        self,
        user: User,
        resource_manager: ResourceManager,
        viewmodel: Mock,
        export_config_state: CurrentExportConfigState,
    ) -> None:
        export_config_state.count_intervals = {TEST_INTERVAL, TEST_SECOND_INTERVAL}
        dialog = build_dialog(resource_manager, viewmodel, export_config_state)
        open_dialog(dialog)

        await user.open(ENDPOINT_NAME)
        dialog._interval_field.set_value(str(TEST_SECOND_INTERVAL))  # type: ignore

        assert dialog.get_specification().interval_in_minutes == TEST_SECOND_INTERVAL

    @pytest.mark.asyncio
    async def test_get_specification(
        self,
        user: User,
        export_counts_dialog: ExportCountsDialog,
        export_config_state: CurrentExportConfigState,
    ) -> None:
        export_config_state.save_name = TEST_SAVE_NAME
        export_config_state.counting_event = CountingEvent.END
        open_dialog(export_counts_dialog)

        await user.open(ENDPOINT_NAME)

        user.find(MARKER_DIRECTORY).clear().type(str(Path(TEST_OUTPUT_FILE).parent))
        user.find(marker=MARKER_APPLY).click()

        specification = export_counts_dialog.get_specification()

        assert specification.start == TEST_START
        assert specification.end == TEST_END
        assert specification.output_format == TEST_DEFAULT_FORMAT
        assert specification.export_directory == Path(TEST_OUTPUT_FILE).parent
        assert specification.export_filename_stem == TEST_SAVE_NAME
        assert specification.export_mode == OVERWRITE
        assert specification.interval_in_minutes == TEST_INTERVAL
        assert specification.counting_event == CountingEvent.END

    @pytest.mark.asyncio
    async def test_save_suffix_is_appended_to_save_name(
        self,
        user: User,
        export_counts_dialog: ExportCountsDialog,
        export_config_state: CurrentExportConfigState,
    ) -> None:
        export_config_state.save_name = TEST_SAVE_NAME
        export_config_state.save_suffix = TEST_SAVE_SUFFIX
        open_dialog(export_counts_dialog)

        await user.open(ENDPOINT_NAME)

        specification = export_counts_dialog.get_specification()

        assert (
            specification.export_filename_stem == f"{TEST_SAVE_NAME}_{TEST_SAVE_SUFFIX}"
        )

    @pytest.mark.asyncio
    async def test_unnamed_export_falls_back_to_suggested_stem(
        self,
        user: User,
        export_counts_dialog: ExportCountsDialog,
    ) -> None:
        open_dialog(export_counts_dialog)

        await user.open(ENDPOINT_NAME)

        specification = export_counts_dialog.get_specification()

        assert specification.export_filename_stem == TEST_FILE_STEM

    @pytest.mark.asyncio
    async def test_different_export_format(
        self,
        user: User,
        resource_manager: ResourceManager,
        viewmodel: Mock,
        export_config_state: CurrentExportConfigState,
    ) -> None:
        dialog = build_dialog(
            resource_manager, viewmodel, export_config_state, default_format="Excel"
        )
        open_dialog(dialog)

        await user.open(ENDPOINT_NAME)

        user.find(MARKER_DIRECTORY).clear().type(
            str(Path(TEST_EXCEL_OUTPUT_FILE).parent)
        )
        user.find(marker=MARKER_APPLY).click()

        specification = dialog.get_specification()

        assert specification.output_format == "Excel"
        assert specification.export_directory == Path(TEST_EXCEL_OUTPUT_FILE).parent

    @pytest.mark.asyncio
    async def test_validation_error_empty_filename(
        self,
        user: User,
        resource_manager: ResourceManager,
        viewmodel: Mock,
        export_config_state: CurrentExportConfigState,
    ) -> None:
        """Test that validation errors are handled correctly for empty filename."""
        viewmodel.get_save_path_suggestion.return_value = SavePathSuggestion(
            save_directory=Path(TEST_FILE_DIR),
            file_stem="",
            context_file_type=TEST_CONTEXT_FILE_TYPE,
            file_type=".csv",
        )
        dialog = build_dialog(resource_manager, viewmodel, export_config_state)
        open_dialog(dialog)

        await user.open(ENDPOINT_NAME)

        with pytest.raises(ValueError, match="No output file selected"):
            dialog.get_specification()

    @pytest.mark.asyncio
    async def test_validation_error_missing_dates(
        self,
        user: User,
        resource_manager: ResourceManager,
        viewmodel: Mock,
        export_config_state: CurrentExportConfigState,
    ) -> None:
        """Test that validation errors are handled correctly for missing dates."""
        dialog = build_dialog(
            resource_manager, viewmodel, export_config_state, start=None, end=None
        )
        open_dialog(dialog)

        await user.open(ENDPOINT_NAME)

        user.find(MARKER_DIRECTORY).clear().type(str(Path(TEST_OUTPUT_FILE).parent))
        user.find(marker=MARKER_APPLY).click()

        with pytest.raises(ValueError, match="Start and end times must be specified"):
            dialog.get_specification()
