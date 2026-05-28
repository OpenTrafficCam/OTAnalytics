from pathlib import Path
from typing import Any

from nicegui import ui

from OTAnalytics.application.files import ensure_dot_in_extension, strip_extension
from OTAnalytics.application.resources.resource_manager import (
    FileChooserDialogKeys,
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

MARKER_FORMAT = "marker-format"
MARKER_FILENAME = "marker-filename"
MARKER_FILENAME_STEM = "marker-filename-stem"
MARKER_FILENAME_SUFFIX = "marker-filename-suffix"
MARKER_DIRECTORY = "marker-directory"


class FileChooserDialog(BaseDialog):
    """Dialog for choosing a file to save or open.

    The dialog operates in three modes depending on the combination of
    ``enforce_suffix`` and ``context_file_type``:

    - ``enforce_suffix=False`` (open mode): a single editable filename field is
      shown. Used by ``askopenfilename``.
    - ``enforce_suffix=True`` and empty ``context_file_type`` (plain save
      mode): a stem field plus a non-editable suffix badge that mirrors the
      currently selected format extension.
    - ``enforce_suffix=True`` and non-empty ``context_file_type`` (context
      export mode): the suffix badge mirrors ``.<context_file_type>.<ext>``.
    """

    def __init__(
        self,
        resource_manager: ResourceManager,
        title: str,
        file_extensions: dict[str, str],
        initial_file_stem: str,
        initial_dir: Path = Path.home(),
        extension_options: dict[str, list[str] | None] | None = None,
        context_file_type: str = "",
        enforce_suffix: bool = False,
    ) -> None:
        """Initialise the dialog.

        Args:
            resource_manager: Provides localised labels for form fields.
            title: Title shown at the top of the dialog.
            file_extensions: Mapping of human-readable format name to the
                extension string used for that format (with or without a
                leading dot).
            initial_file_stem: Default filename stem (no extension).
            initial_dir: Directory to open the dialog in.
            extension_options: Optional per-format file picker options
                forwarded to ``LocalFilePicker``.
            context_file_type: Optional context type token (e.g. ``"events"``)
                inserted between stem and extension in the locked suffix.
                Only meaningful when ``enforce_suffix`` is ``True``.
            enforce_suffix: When ``True``, render a stem field plus a
                non-editable locked suffix derived from the selected format
                and ``context_file_type``. When ``False`` (default), render
                the legacy single editable filename field used for open
                dialogs and not-yet-migrated callers.
        """
        super().__init__(resource_manager)
        self._title = title
        self._file_extensions = file_extensions
        self._initial_file_stem = initial_file_stem
        self._initial_dir = initial_dir
        self._extension_options = extension_options
        self._context_file_type = context_file_type
        self._enforce_suffix = enforce_suffix

        self._format_field = FormFieldSelect(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_FORMAT),
            options=list(file_extensions.keys()),
            initial_value=(
                list(file_extensions.keys())[0] if file_extensions else None
            ),
            on_value_change=self._on_format_change,
            marker=MARKER_FORMAT,
        )

        self._filename_field: FormFieldText | None = None
        self._filename_stem_field: FormFieldText | None = None
        self._filename_suffix_field: FormFieldText | None = None

        if self._enforce_suffix:
            self._filename_stem_field = FormFieldText(
                label_text=self.resource_manager.get(
                    FileChooserDialogKeys.LABEL_FILENAME
                ),
                initial_value=initial_file_stem,
                marker=MARKER_FILENAME_STEM,
            )
            self._filename_suffix_field = FormFieldText(
                label_text="",
                initial_value=self._build_locked_suffix(),
                readonly=True,
                marker=MARKER_FILENAME_SUFFIX,
            )
        else:
            self._filename_field = FormFieldText(
                label_text=self.resource_manager.get(
                    FileChooserDialogKeys.LABEL_FILENAME
                ),
                initial_value=(
                    f"{initial_file_stem}" f"{self._get_extension_for_current_format()}"
                ),
                marker=MARKER_FILENAME,
            )

        self._directory_field = FormFieldText(
            label_text=self.resource_manager.get(FileChooserDialogKeys.LABEL_DIRECTORY),
            initial_value=str(initial_dir),
            on_value_change=self._update_directory,
            marker=MARKER_DIRECTORY,
        )

    def build_content(self) -> None:
        ui.label(self._title).classes("text-xl")

        with ui.column().classes("w-full"):
            self._format_field.build()
            if self._enforce_suffix:
                assert self._filename_stem_field is not None
                assert self._filename_suffix_field is not None
                with ui.row().classes("w-full no-wrap items-end"):
                    self._filename_stem_field.build()
                    self._filename_suffix_field.build()
            else:
                assert self._filename_field is not None
                self._filename_field.build()
            self._directory_field.build()

            with ui.row():
                ui.button(
                    self.resource_manager.get(FileChooserDialogKeys.LABEL_BROWSE),
                    on_click=self._browse_directory,
                )

    def _on_format_change(self, _: Any) -> None:
        if self._enforce_suffix:
            assert self._filename_suffix_field is not None
            self._filename_suffix_field.set_value(self._build_locked_suffix())
        else:
            assert self._filename_field is not None
            current_filename = self._filename_field.value
            filename_stem = Path(current_filename).stem
            new_extension = self._get_extension_for_current_format()
            self._filename_field.set_value(f"{filename_stem}{new_extension}")

    def _build_locked_suffix(self) -> str:
        ext = ensure_dot_in_extension(self._get_extension_for_current_format())
        if self._context_file_type:
            return f".{self._context_file_type}{ext}"
        return ext

    def _get_extension_for_current_format(self) -> str:
        if not self._file_extensions:
            return ""
        try:
            selected_format = self._format_field.value
        except MissingInstanceError:
            selected_format = list(self._file_extensions.keys())[0]
        return ensure_dot_in_extension(self._file_extensions[selected_format])

    def _update_directory(self, e: Any) -> None:
        if not e.value:
            return
        try:
            new_path = Path(e.value).expanduser()
            if new_path.exists() and new_path.is_dir():
                self._initial_dir = new_path
        except Exception:
            self._directory_field.set_value(str(self._initial_dir))

    async def _browse_directory(self) -> None:
        picker = LocalFilePicker(
            directory=Path(self._directory_field.value),
            show_hidden_files=False,
            show_files_only_of_type=None,
            show_only_directories=False,
            extension_options=self._extension_options,
        )
        result = await picker
        if result and result[0]:
            selected_path = result[0]
            if selected_path.is_dir():
                self._directory_field.set_value(str(selected_path))
            else:
                self._directory_field.set_value(str(selected_path.parent))
                self._set_filename_from_picked(selected_path.name)

    def _set_filename_from_picked(self, picked_name: str) -> None:
        if self._enforce_suffix:
            assert self._filename_stem_field is not None
            suffix = self._build_locked_suffix()
            if picked_name.endswith(suffix):
                self._filename_stem_field.set_value(
                    strip_extension(picked_name, suffix)
                )
            else:
                self._filename_stem_field.set_value(Path(picked_name).stem)
        else:
            assert self._filename_field is not None
            self._filename_field.set_value(picked_name)

    def get_directory(self) -> Path:
        """Return the currently selected directory.

        Returns:
            The directory field value as a ``Path``.
        """
        return Path(self._directory_field.value)

    def get_file_stem(self) -> str:
        """Return the filename stem (without the locked suffix or extension).

        In ``enforce_suffix`` mode, returns the value of the stem field
        directly. In open mode (legacy single-field), returns
        ``Path(filename).stem``.

        Returns:
            The current stem as a string.
        """
        if self._enforce_suffix:
            assert self._filename_stem_field is not None
            return self._filename_stem_field.value
        assert self._filename_field is not None
        return Path(self._filename_field.value).stem

    def get_export_format_extension(self) -> str:
        """Return the leading-dot file extension for the selected format.

        Returns:
            The extension including a leading dot (e.g. ``".csv"``).
        """
        return self._get_extension_for_current_format()

    def get_file_path(self) -> Path:
        """Return the full path assembled from directory, stem and suffix.

        In ``enforce_suffix`` mode, combines the directory, stem field and
        locked suffix field. In open mode, combines the directory and the
        single editable filename field.

        Returns:
            The composed ``Path``.
        """
        if self._enforce_suffix:
            assert self._filename_stem_field is not None
            assert self._filename_suffix_field is not None
            return self.get_directory() / (
                self._filename_stem_field.value + self._filename_suffix_field.value
            )
        assert self._filename_field is not None
        return self.get_directory() / self._filename_field.value

    def get_format(self) -> str:
        """Return the human-readable name of the selected format.

        Returns:
            The selected format key, or an empty string when no formats are
            configured.
        """
        if not self._file_extensions:
            return ""
        return self._format_field.value
