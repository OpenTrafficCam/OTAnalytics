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
    FormFieldText,
)

MARKER_START_DATE = "marker-start-date"
MARKER_START_TIME = "marker-start-time"
MARKER_END_DATE = "marker-end-date"
MARKER_END_TIME = "marker-end-time"
MARKER_DIRECTORY = "marker-directory"
MARKER_FILENAME = "marker-filename"
MARKER_INTERVAL = "marker-interval"


class ExportCountsDialog(BaseDialog):
    """Dialog for configuring export counts.

    This dialog allows the user to configure the parameters for exporting counts.
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
            initial_dir (Path): The initial directory for file selection, defaults to
                user's home directory
        """
        super().__init__(resource_manager)
        self._viewmodel = viewmodel
        self._export_formats = export_formats
        self._default_format = default_format
        self._modes = modes

        # Create form fields
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
            initial_value=15,  # Default interval of 15 minutes
            min_value=1,
            marker=MARKER_INTERVAL,
        )

        self._directory_field = FormFieldText(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_DIRECTORY),
            initial_value=str(initial_dir),
            on_value_change=self._update_directory,
            marker=MARKER_DIRECTORY,
        )

        self._initial_dir = initial_dir

        # Generate a suggested filename
        extension = self._export_formats[self._default_format].lstrip(".")
        interval_value = self._interval.initial_value
        context_file_type = f"{CONTEXT_FILE_TYPE_COUNTS}_{interval_value}{DEFAULT_COUNT_INTERVAL_TIME_UNIT}"  # noqa
        suggested_path = self._viewmodel.get_save_path_suggestion(
            extension, context_file_type
        )
        suggested_stem = Path(suggested_path.name).stem
        suggested_filename = f"{suggested_stem}.{extension}"

        self._filename_field = FormFieldText(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_FILENAME),
            initial_value=suggested_filename,
            marker=MARKER_FILENAME,
        )

    def build_content(self) -> None:
        """Build the dialog content."""
        ui.label(
            self.resource_manager.get(ExportCountsDialogKeys.LABEL_EXPORT_COUNTS)
        ).classes("text-xl")

        with ui.column().classes("w-full"):
            # Time range section
            ui.label(
                self.resource_manager.get(ExportCountsDialogKeys.LABEL_TIME_RANGE)
            ).classes("text-lg")
            self._start_datetime.build()
            self._end_datetime.build()
            self._interval.build()

            # Output file section
            ui.label(
                self.resource_manager.get(ExportCountsDialogKeys.LABEL_OUTPUT_FILE)
            ).classes("text-lg")
            self._directory_field.build()
            self._filename_field.build()
            with ui.row():
                ui.button(
                    self.resource_manager.get(FileChooserDialogKeys.LABEL_BROWSE),
                    on_click=self._select_output_file,
                )

    def _update_directory(self, e: Any) -> None:
        """Update the directory based on user input."""
        try:
            new_path = Path(e.value).expanduser()
            if new_path.exists() and new_path.is_dir():
                # Path is valid, update the initial_dir attribute
                self._initial_dir = new_path
            else:
                # If path doesn't exist or is not a directory, revert to current path
                self._directory_field.set_value(str(self._initial_dir))
        except Exception:
            # If there's any error, revert to initial directory
            self._directory_field.set_value(str(self._initial_dir))

    async def _select_output_file(self) -> None:
        """Open a dialog to browse for a directory."""
        await select_output_directory(
            directory=Path(self._directory_field.value),
            set_directory_callback=self._directory_field.set_value,
        )

    def get_file_path(self) -> Path:
        """Get the selected file path."""
        return Path(self._directory_field.value) / self._filename_field.value

    def get_specification(self) -> CountingSpecificationDto:
        """Get the export specification."""
        if not self._filename_field.value:
            raise ValueError("No output file selected")

        if not self._start_datetime.value or not self._end_datetime.value:
            raise ValueError("Start and end times must be specified")

        return CountingSpecificationDto(
            start=self._start_datetime.value,
            end=self._end_datetime.value,
            interval_in_minutes=self._interval.value,
            modes=[self._modes[0]] if self._modes else [],
            output_format=self._default_format,
            output_file=str(self.get_file_path()),
            export_mode=OVERWRITE,
        )
