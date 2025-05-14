from pathlib import Path
from typing import Any

from nicegui import ui

from OTAnalytics.application.resources.resource_manager import (
    GeneralKeys,
    ResourceManager,
)
from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker import LocalFilePicker
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.dialog import BaseDialog
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.forms import (
    FormFieldSelect,
    FormFieldText,
)
from OTAnalytics.plugin_ui.nicegui_gui.nicegui.elements.table import (
    MissingInstanceError,
)


class FileChooserDialog(BaseDialog):
    "Dialog for choosing a file to save or open."

    def __init__(
        self,
        resource_manager: ResourceManager,
        title: str,
        file_extensions: dict[str, str],
        initial_file_stem: str,
        initial_dir: Path = Path.home(),
    ) -> None:
        """Initialize the file chooser dialog.

        Args:
            resource_manager: The resource manager for localization
            title: The title of the dialog
            file_extensions: A dictionary mapping format names to file extensions
            initial_file_stem: The initial file name without extension
            initial_dir: The initial directory to show
        """
        super().__init__(resource_manager)
        self._title = title
        self._file_extensions = file_extensions
        self._initial_file_stem = initial_file_stem
        self._initial_dir = initial_dir

        # Create form fields
        self._format_field = FormFieldSelect(
            label_text=self.resource_manager.get(GeneralKeys.LABEL_FORMAT),
            options=list(file_extensions.keys()),
            initial_value=list(file_extensions.keys())[0] if file_extensions else None,
            on_value_change=self._update_file_extension,
        )

        self._filename_field = FormFieldText(
            label_text=self.resource_manager.get(GeneralKeys.LABEL_FILENAME),
            initial_value=f"{initial_file_stem}{self._get_extension_for_current_format()}",  # noqa
        )

        self._directory_field = FormFieldText(
            label_text=self.resource_manager.get(GeneralKeys.LABEL_DIRECTORY),
            initial_value=str(initial_dir),
            on_value_change=self._update_directory,
        )

    def build_content(self) -> None:
        """Build the dialog content."""
        ui.label(self._title).classes("text-xl")

        with ui.column().classes("w-full"):
            self._format_field.build()
            self._filename_field.build()
            self._directory_field.build()

            with ui.row():
                ui.button(
                    self.resource_manager.get(GeneralKeys.LABEL_BROWSE),
                    on_click=self._browse_directory,
                )

    def _update_file_extension(self, _: Any) -> None:
        """Update the file extension based on the selected format."""
        current_filename = self._filename_field.value
        # Remove the old extension if present
        filename_stem = Path(current_filename).stem
        new_extension = self._get_extension_for_current_format()
        self._filename_field.set_value(f"{filename_stem}.{new_extension}")

    def _get_extension_for_current_format(self) -> str:
        """Get the file extension for the currently selected format."""
        try:
            selected_format = self._format_field.value
        except MissingInstanceError:
            # If _format_field hasn't been built yet, use the first format
            selected_format = list(self._file_extensions.keys())[0]
        return self._file_extensions[selected_format]

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

    async def _browse_directory(self) -> None:
        """Open a dialog to browse for a directory."""
        # Use LocalFilePicker to browse for a directory
        picker = LocalFilePicker(
            directory=Path(self._directory_field.value),
            show_hidden_files=False,
            show_only_directories=True,
        )
        result = await picker
        if result and result[0]:
            # If the selected path is a directory, use it directly
            # Otherwise, use its parent directory
            selected_path = result[0]
            if selected_path.is_dir():
                self._directory_field.set_value(str(selected_path))
            else:
                self._directory_field.set_value(str(selected_path.parent))

    def get_file_path(self) -> Path:
        """Get the selected file path."""
        return Path(self._directory_field.value) / self._filename_field.value

    def get_format(self) -> str:
        """Get the selected format."""
        return self._format_field.value
