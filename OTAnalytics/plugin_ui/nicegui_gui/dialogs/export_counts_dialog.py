from datetime import datetime
from pathlib import Path
from typing import Any

from nicegui import ui

from OTAnalytics.adapter_ui.helpers import ensure_dot_in_extension, strip_extension
from OTAnalytics.adapter_ui.view_model import ViewModel
from OTAnalytics.application.analysis.traffic_counting_specification import (
    CountingEvent,
    CountingSpecificationDto,
)
from OTAnalytics.application.config import (
    CONTEXT_FILE_TYPE_COUNTS,
    DEFAULT_COUNT_INTERVAL_TIME_UNIT,
)
from OTAnalytics.application.export_formats.export_mode import OVERWRITE
from OTAnalytics.application.resources.resource_manager import (
    ExportCountsDialogKeys,
    FileChooserDialogKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.file_utils import select_output_directory
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import BaseDialog
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import (
    DateTimeForm,
    FormFieldInteger,
    FormFieldSelect,
    FormFieldText,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import (
    MissingInstanceError,
)

MARKER_START_DATE = "marker-start-date"
MARKER_START_TIME = "marker-start-time"
MARKER_END_DATE = "marker-end-date"
MARKER_END_TIME = "marker-end-time"
MARKER_DIRECTORY = "marker-directory"
MARKER_FILENAME_STEM = "marker-filename-stem"
MARKER_FILENAME_SUFFIX = "marker-filename-suffix"
MARKER_FORMAT = "marker-format"
MARKER_INTERVAL = "marker-interval"
MARKER_COUNTING_EVENT = "marker-counting-event"

DEFAULT_INTERVAL_MINUTES = 15


class ExportCountsDialog(BaseDialog):
    """Dialog for configuring counts export.

    Uses a stem field plus a non-editable suffix badge that reflects
    ``.counts_<interval>min.<ext>``. Interval and format changes update the
    badge live.
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
        initial_dir: Path = Path.home(),
    ) -> None:
        """Initialise the dialog.

        Args:
            resource_manager: The resource manager for localised labels.
            viewmodel: The application view model.
            start: Start datetime for the count window (may be None).
            end: End datetime for the count window (may be None).
            default_format: The format name selected by default.
            modes: Counting modes to include in the produced specification.
            export_formats: Mapping of format name to file extension.
            initial_dir: Initial directory, used if no save-path suggestion
                is available.
        """
        super().__init__(resource_manager)
        self._viewmodel = viewmodel
        self._export_formats = export_formats
        self._default_format = default_format
        self._modes = modes
        self._initial_dir = initial_dir

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

        self._interval = FormFieldInteger(
            label_text=self.resource_manager.get(
                ExportCountsDialogKeys.LABEL_INTERVAL_MINUTES
            ),
            initial_value=DEFAULT_INTERVAL_MINUTES,
            min_value=1,
            on_value_change=self._on_interval_or_format_change,
            marker=MARKER_INTERVAL,
        )

        suggestion = self._viewmodel.get_save_path_suggestion(
            self._extension_for_default_format().lstrip("."),
            self._context_for_current_interval(DEFAULT_INTERVAL_MINUTES),
        )
        initial_stem = strip_extension(
            suggestion.stem,
            f".{self._context_for_current_interval(DEFAULT_INTERVAL_MINUTES)}",
        )

        self._directory_field = FormFieldText(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_DIRECTORY),
            initial_value=str(suggestion.parent),
            on_value_change=self._update_directory,
            marker=MARKER_DIRECTORY,
        )

        self._format_field = FormFieldSelect(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_FORMAT),
            options=list(export_formats.keys()),
            initial_value=default_format,
            on_value_change=self._on_interval_or_format_change,
            marker=MARKER_FORMAT,
        )

        self._filename_stem_field = FormFieldText(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_FILENAME),
            initial_value=initial_stem,
            marker=MARKER_FILENAME_STEM,
        )
        self._filename_suffix_field = FormFieldText(
            label_text="",
            initial_value=self._build_locked_suffix(DEFAULT_INTERVAL_MINUTES),
            readonly=True,
            marker=MARKER_FILENAME_SUFFIX,
        )

        self._counting_event_field = FormFieldSelect(
            label_text=self.resource_manager.get(
                ExportCountsDialogKeys.LABEL_COUNTING_EVENT
            ),
            options=[event.value for event in CountingEvent],
            initial_value=CountingEvent.START.value,
            marker=MARKER_COUNTING_EVENT,
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
            self._interval.build()
            self._counting_event_field.build()

            ui.label(
                self.resource_manager.get(ExportCountsDialogKeys.LABEL_OUTPUT_FILE)
            ).classes("text-lg")
            self._format_field.build()
            with ui.row().classes("w-full no-wrap items-end"):
                self._filename_stem_field.build()
                self._filename_suffix_field.build()
            self._directory_field.build()
            with ui.row():
                ui.button(
                    self.resource_manager.get(FileChooserDialogKeys.LABEL_BROWSE),
                    on_click=self._select_output_file,
                )

    def _extension_for_default_format(self) -> str:
        return ensure_dot_in_extension(self._export_formats[self._default_format])

    def _current_extension(self) -> str:
        try:
            selected_format = self._format_field.value
        except MissingInstanceError:
            selected_format = self._default_format
        return ensure_dot_in_extension(self._export_formats[selected_format])

    def _context_for_current_interval(self, interval: int) -> str:
        return (
            f"{CONTEXT_FILE_TYPE_COUNTS}_{interval}"
            f"{DEFAULT_COUNT_INTERVAL_TIME_UNIT}"
        )

    def _build_locked_suffix(self, interval: int) -> str:
        return (
            f".{self._context_for_current_interval(interval)}"
            f"{self._current_extension()}"
        )

    def _on_interval_or_format_change(self, _: Any) -> None:
        try:
            interval = self._interval.value
        except MissingInstanceError:
            interval = DEFAULT_INTERVAL_MINUTES
        self._filename_suffix_field.set_value(self._build_locked_suffix(interval))

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

    def get_file_path(self) -> Path:
        """Return the full file path composed from directory + stem + suffix."""
        return Path(self._directory_field.value) / (
            self._filename_stem_field.value + self._filename_suffix_field.value
        )

    def get_selected_directory(self) -> Path:
        """Return the currently selected output directory."""
        return Path(self._directory_field.value)

    def get_selected_filename(self) -> str:
        """Return the full filename (stem + locked suffix)."""
        return self._filename_stem_field.value + self._filename_suffix_field.value

    def get_specification(self) -> CountingSpecificationDto:
        """Build the CountingSpecificationDto from the current dialog state.

        Raises:
            ValueError: If the stem is empty or either datetime is missing.

        Returns:
            A populated CountingSpecificationDto using the new
            ``export_directory`` / ``export_filename_stem`` contract.
        """
        if not self._filename_stem_field.value:
            raise ValueError("No output file selected")

        if not self._start_datetime.value or not self._end_datetime.value:
            raise ValueError("Start and end times must be specified")

        file_path = self.get_file_path()
        return CountingSpecificationDto(
            start=self._start_datetime.value,
            end=self._end_datetime.value,
            interval_in_minutes=self._interval.value,
            modes=[self._modes[0]] if self._modes else [],
            output_format=self._format_field.value,
            export_directory=file_path.parent,
            export_filename_stem=self._filename_stem_field.value,
            export_mode=OVERWRITE,
            counting_event=CountingEvent.parse(self._counting_event_field.value),
        )
