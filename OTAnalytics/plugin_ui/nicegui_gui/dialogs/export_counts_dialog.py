from datetime import datetime
from pathlib import Path
from typing import Any

from nicegui import ui

from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingSpecificationDto,
)
from OTAnalytics.application.config import (
    CONTEXT_FILE_TYPE_COUNTS,
    DEFAULT_COUNT_INTERVAL_TIME_UNIT,
    DEFAULT_COUNTING_INTERVAL_IN_MINUTES,
)
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.files import ensure_dot_in_extension
from OTAnalytics.application.resources.resource_manager import (
    ExportCountsDialogKeys,
    FileChooserDialogKeys,
    ResourceManager,
)
from OTAnalytics.application.use_cases.static_analysis_config import (
    GetCountingEventOfCurrentAnalysisConfig,
    GetCountIntervalsOfCurrentAnalysisConfig,
    GetSaveNameOfCurrentAnalysisConfig,
    GetSaveSuffixOfCurrentAnalysisConfig,
)
from OTAnalytics.plugin_ui.nicegui_gui.file_utils import select_output_directory
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import BaseDialog
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import (
    DateTimeForm,
    FormFieldSelect,
    FormFieldText,
)

MARKER_START_DATE = "marker-start-date"
MARKER_START_TIME = "marker-start-time"
MARKER_END_DATE = "marker-end-date"
MARKER_END_TIME = "marker-end-time"
MARKER_DIRECTORY = "marker-directory"
MARKER_FORMAT = "marker-format"
MARKER_INTERVAL = "marker-interval"

SAVE_SUFFIX_SEPARATOR = "_"


class ExportCountsDialog(BaseDialog):
    """Dialog for configuring counts export.

    Everything the analysis configuration already defines is read from
    there instead of being asked for again. Only the count interval is
    offered as a choice, when there is more than one configured.
    """

    def __init__(
        self,
        resource_manager: ResourceManager,
        viewmodel: ViewModel,
        start: datetime | None,
        end: datetime | None,
        default_format: str,
        modes: list,
        export_formats: dict[str, str],
        get_count_intervals: GetCountIntervalsOfCurrentAnalysisConfig,
        get_counting_event: GetCountingEventOfCurrentAnalysisConfig,
        get_save_name: GetSaveNameOfCurrentAnalysisConfig,
        get_save_suffix: GetSaveSuffixOfCurrentAnalysisConfig,
        initial_dir: Path = Path.home(),
    ) -> None:
        """Initialize the export counts dialog.

        Args:
            resource_manager (ResourceManager): The resource manager for localization
            viewmodel (ViewModel): The view model
            start (datetime | None): The start datetime
            end (datetime | None): The end datetime
            default_format (str): The default export format
            modes (list): The available export modes
            export_formats (dict[str, str]): A dictionary mapping format names to file
                extensions
            get_count_intervals (GetCountIntervalsOfCurrentAnalysisConfig): provides
                the configured count intervals in minutes
            get_counting_event (GetCountingEventOfCurrentAnalysisConfig): provides
                the configured counting event
            get_save_name (GetSaveNameOfCurrentAnalysisConfig): provides the
                configured name the results are saved under
            get_save_suffix (GetSaveSuffixOfCurrentAnalysisConfig): provides the
                configured suffix appended to the save name
            initial_dir (Path): The initial directory for file selection, defaults to
                user's home directory
        """
        super().__init__(resource_manager)
        self._viewmodel = viewmodel
        self._export_formats = export_formats
        self._default_format = default_format
        self._modes = modes
        self._initial_dir = initial_dir
        self._get_count_intervals = get_count_intervals
        self._get_counting_event = get_counting_event
        self._get_save_name = get_save_name
        self._get_save_suffix = get_save_suffix

        self._start_datetime = DateTimeForm(
            label_date_text=self.resource_manager.get(
                ExportCountsDialogKeys.LABEL_START_DATE
            ),
            label_time_text=self.resource_manager.get(
                ExportCountsDialogKeys.LABEL_START_TIME
            ),
            initial_value=start,
            marker_date=MARKER_START_DATE,
            marker_time=MARKER_START_TIME,
        )

        self._end_datetime = DateTimeForm(
            label_date_text=self.resource_manager.get(
                ExportCountsDialogKeys.LABEL_END_DATE
            ),
            label_time_text=self.resource_manager.get(
                ExportCountsDialogKeys.LABEL_END_TIME
            ),
            initial_value=end,
            marker_date=MARKER_END_DATE,
            marker_time=MARKER_END_TIME,
        )

        configured_intervals = self._configured_intervals()
        self._interval_field: FormFieldSelect | None = None
        if len(configured_intervals) > 1:
            self._interval_field = FormFieldSelect(
                label_text=self.resource_manager.get(
                    ExportCountsDialogKeys.LABEL_INTERVAL_MINUTES
                ),
                options=[str(interval) for interval in configured_intervals],
                initial_value=str(configured_intervals[0]),
                marker=MARKER_INTERVAL,
            )

        suggestion = self._viewmodel.get_save_path_suggestion(
            file_type=self._extension_for_default_format(),
            context_file_type=self._context_for_interval(configured_intervals[0]),
        )
        self._suggested_file_stem = suggestion.file_stem

        self._directory_field = FormFieldText(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_DIRECTORY),
            initial_value=str(suggestion.save_directory),
            on_value_change=self._update_directory,
            marker=MARKER_DIRECTORY,
        )

        self._format_field = FormFieldSelect(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_FORMAT),
            options=list(export_formats.keys()),
            initial_value=default_format,
            marker=MARKER_FORMAT,
        )

    def build_content(self) -> None:
        """Build the dialog's content elements."""
        ui.label(
            self.resource_manager.get(ExportCountsDialogKeys.LABEL_EXPORT_COUNTS)
        ).classes("text-xl")

        with ui.column().classes("w-full"):
            ui.label(
                self.resource_manager.get(ExportCountsDialogKeys.LABEL_TIME_RANGE)
            ).classes("text-lg")
            self._start_datetime.build()
            self._end_datetime.build()
            if self._interval_field:
                self._interval_field.build()

            ui.label(
                self.resource_manager.get(ExportCountsDialogKeys.LABEL_OUTPUT_FILE)
            ).classes("text-lg")
            self._format_field.build()
            self._directory_field.build()
            with ui.row():
                ui.button(
                    self.resource_manager.get(FileChooserDialogKeys.LABEL_BROWSE),
                    on_click=self._select_output_file,
                )

    def _configured_intervals(self) -> list[int]:
        """Provide the configured count intervals, smallest one first.

        A configuration without any interval falls back to the application
        default, so the dialog can always name an interval.

        Returns:
            list[int]: the count intervals in minutes.
        """
        if intervals := sorted(self._get_count_intervals.get()):
            return intervals
        return [DEFAULT_COUNTING_INTERVAL_IN_MINUTES]

    def _selected_interval(self) -> int:
        if self._interval_field is None:
            return self._configured_intervals()[0]
        return int(self._interval_field.value)

    def _export_filename_stem(self) -> str:
        """Build the file stem from the configured save name and suffix.

        Mirrors how a cli run composes its save stem. A project that does not
        name its exports keeps the suggested stem, so exporting stays possible
        without configuring a name first.

        Returns:
            str: the file stem to export under.
        """
        save_name = self._get_save_name.get()
        stem = Path(save_name).stem if save_name else self._suggested_file_stem
        if save_suffix := self._get_save_suffix.get():
            return f"{stem}{SAVE_SUFFIX_SEPARATOR}{save_suffix}"
        return stem

    def _extension_for_default_format(self) -> str:
        return ensure_dot_in_extension(self._export_formats[self._default_format])

    def _context_for_interval(self, interval: int) -> str:
        return (
            f"{CONTEXT_FILE_TYPE_COUNTS}_{interval}"
            f"{DEFAULT_COUNT_INTERVAL_TIME_UNIT}"
        )

    def _update_directory(self, e: Any) -> None:
        if not e.value:
            return
        try:
            new_path = Path(e.value).expanduser()
            if new_path.exists() and new_path.is_dir():
                self._initial_dir = new_path
        except Exception:
            self._directory_field.set_value(str(self._initial_dir))

    async def _select_output_file(self) -> None:
        await select_output_directory(
            directory=Path(self._directory_field.value),
            set_directory_callback=self._directory_field.set_value,
        )

    def get_selected_directory(self) -> Path:
        """Return the currently selected output directory."""
        return Path(self._directory_field.value)

    def get_specification(self) -> CountingSpecificationDto:
        """Build the CountingSpecificationDto from the current dialog state.

        Raises:
            ValueError: If no file stem can be determined or either datetime is
                missing.

        Returns:
            A populated CountingSpecificationDto using the new
            ``export_directory`` / ``export_filename_stem`` contract.
        """
        export_filename_stem = self._export_filename_stem()
        if not export_filename_stem:
            raise ValueError("No output file selected")

        if not self._start_datetime.value or not self._end_datetime.value:
            raise ValueError("Start and end times must be specified")

        return CountingSpecificationDto(
            start=self._start_datetime.value,
            end=self._end_datetime.value,
            interval_in_minutes=self._selected_interval(),
            modes=[self._modes[0]] if self._modes else [],
            output_format=self._format_field.value,
            export_directory=self.get_selected_directory(),
            export_filename_stem=export_filename_stem,
            export_mode=OVERWRITE,
            counting_event=self._get_counting_event.get(),
        )
