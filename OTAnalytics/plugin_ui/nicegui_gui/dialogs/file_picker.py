import platform
from pathlib import Path
from typing import Any, Dict, List, Optional

from nicegui import events, ui

OK_BUTTON_NAME: str = "Ok"
CANCEL_BUTTON_NAME: str = "Cancel"
DATA: str = "data"
NAME: str = "name"
PATH: str = "path"
FILE: str = "File"
ROW_DATA: str = "rowData"
NULL_TERMINATOR: str = "\000"


class LocalFilePicker(ui.dialog):

    def __init__(
        self,
        directory: Path,
        *,
        multiple: bool = False,
        show_hidden_files: bool = False,
        show_files_only_of_type: str | None = None,
        show_files_only_of_types: list[str] | None = None,
        show_only_directories: bool = False,
        show_extension_select: bool = True,
        extension_options: Dict[str, Optional[List[str]]] | None = None,
    ) -> None:
        """Local File Picker

        This is a simple file picker that allows you to select a file from the local
        filesystem where NiceGUI is running.

        Args:
            directory (Path): The directory to start in.
            multiple (bool): Whether to allow multiple files to be selected.
            show_hidden_files (bool): Whether to show hidden files.
            show_files_only_of_type (str): Show files only of type specified.
                Otherwise, show all files. (Deprecated: use show_files_only_of_types)
            show_files_only_of_types (list[str]): Show files only of types specified.
                Otherwise, show all files.
            show_only_directories (bool): Whether to show only directories.
                If True, files will not be shown in the picker.
            show_extension_select (bool): Whether to show a dropdown
            to select file extensions.
                If True, a select dropdown will be
                displayed to filter files by extension.
            extension_options (Dict[str, Optional[List[str]]]): Custom extension options
                for the dropdown selector. Keys are display names, values are lists of
                extensions or None for "All Files". If None, uses default options.
        """
        super().__init__()

        self.path: Path = directory.expanduser()
        self.upper_limit: Path = directory.expanduser()
        self.show_hidden_files: bool = show_hidden_files
        self.show_files_only_of_type: Optional[str] = show_files_only_of_type
        self.show_files_only_of_types: Optional[List[str]] = show_files_only_of_types
        self.show_only_directories: bool = show_only_directories
        self.show_extension_select: bool = show_extension_select

        # Define file extension options for the select dropdown
        self.extension_options: Dict[str, Optional[List[str]]] = extension_options or {
            "All Files": None,
            "OTConfig Files": [".otconfig"],
            "OTFlow Files": [".otflow"],
        }

        # Current selected extension filter from dropdown
        self.current_extension_filter: Optional[List[str]] = None
        # Track the currently selected option name to handle "All Files" correctly
        self.current_selected_option: str = "All Files"

        with self, ui.card().style("max-width: 70%; width: 100%"):
            self.add_drives_toggle()
            with ui.row().classes("w-full"):
                self.path_input: ui.input = ui.input(
                    label="Path",
                    value=str(self.path),
                    on_change=self.update_path_from_input,
                ).classes("w-full")

            self.grid: ui.aggrid = ui.aggrid(
                {
                    "columnDefs": [{"field": NAME, "headerName": FILE}],
                    "rowSelection": "multiple" if multiple else "single",
                },
                html_columns=[0],
            ).on("cellDoubleClicked", self.handle_double_click)

            # Add file extension select dropdown at the bottom if enabled
            if self.show_extension_select and not self.show_only_directories:
                with ui.row().classes("w-full"):
                    self.extension_select: ui.select = ui.select(
                        options=list(self.extension_options.keys()),
                        label="File Type Filter",
                        value="All Files",
                        on_change=self.update_extension_filter,
                    ).classes("w-full")
            with ui.row().classes("w-full justify-end"):
                ui.button(CANCEL_BUTTON_NAME, on_click=self.close).props("outline")
                ui.button(OK_BUTTON_NAME, on_click=self._handle_ok)
        self.update_grid()

    def add_drives_toggle(self) -> None:
        if platform.system() == "Windows":
            import win32api

            drives = win32api.GetLogicalDriveStrings().split(NULL_TERMINATOR)[:-1]
            self.drives_toggle: ui.toggle = ui.toggle(
                drives, value=drives[0], on_change=self.update_drive
            )

    def update_drive(self) -> None:
        if hasattr(self, "drives_toggle"):
            self.path = Path(self.drives_toggle.value).expanduser()
            self.path_input.value = str(self.path)
            self.update_grid()

    def update_path_from_input(self, e: Any) -> None:
        try:
            new_path: Path = Path(e.value).expanduser()
            if new_path.exists() and new_path.is_dir():
                self.path = new_path
                self.update_grid()
            else:
                # If path doesn't exist or is not a directory, revert to current path
                self.path_input.value = str(self.path)
        except Exception:
            # If there's any error, revert to current path
            self.path_input.value = str(self.path)

    def update_extension_filter(self, e: Any) -> None:
        """Update the file extension filter based on the selected option."""
        selected_option: str = e.value
        self.current_selected_option = selected_option
        self.current_extension_filter = self.extension_options.get(selected_option)
        self.update_grid()

    def update_grid(self) -> None:
        paths: List[Path] = list(self.path.glob("*"))
        if not self.show_hidden_files:
            paths = [p for p in paths if not p.name.startswith(".")]

        if self.show_only_directories:
            paths = [p for p in paths if p.is_dir()]
        elif self.current_selected_option == "All Files":
            # This ensures that "All Files" overrides any other filtering parameters
            pass  # No additional filtering needed - show all files and directories
        elif self.current_extension_filter is not None:
            # Filter based on the dropdown selection (highest priority)
            paths = [
                p
                for p in paths
                if p.is_file()
                and p.suffix in self.current_extension_filter
                or p.is_dir()
            ]
        elif self.show_files_only_of_types:
            # Support multiple file extensions
            paths = [
                p
                for p in paths
                if p.is_file()
                and p.suffix in self.show_files_only_of_types
                or p.is_dir()
            ]
        elif self.show_files_only_of_type:
            # Backward compatibility for single file extension
            paths = [
                p
                for p in paths
                if p.is_file()
                and p.suffix == self.show_files_only_of_type
                or p.is_dir()
            ]
        paths.sort(key=lambda p: p.name.lower())
        paths.sort(key=lambda p: not p.is_dir())

        self.grid.options[ROW_DATA] = [
            {
                NAME: f"📁 <strong>{p.name}</strong>" if p.is_dir() else p.name,
                PATH: self._map_to_ui(p),
            }
            for p in paths
        ]
        if (
            self.upper_limit is None
            and self.path != self.path.parent
            or self.upper_limit is not None
            and self.path != self.upper_limit
        ):
            self.grid.options[ROW_DATA].insert(
                0,
                {
                    NAME: "📁 <strong>..</strong>",
                    PATH: self._map_to_ui(self.path.parent),
                },
            )
        self.grid.update()

    def handle_double_click(self, e: events.GenericEventArguments) -> None:
        self.path = Path(e.args[DATA][PATH])
        if self.path.is_dir():
            # Always navigate into directories when double-clicked
            self.path_input.value = str(self.path)
            self.update_grid()
        else:
            self.submit([self.path])

    async def _handle_ok(self) -> None:
        rows: List[Dict[str, Any]] = await self.grid.get_selected_rows()
        paths: List[Path] = [self._map_to_domain(r[PATH]) for r in rows]

        # If no rows are selected and we're in directory-only mode, use the current directory # noqa
        if not paths and self.show_only_directories:
            paths = [self.path]

        self.submit(paths)

    def _map_to_domain(self, path: str) -> Path:
        return Path(path)

    def _map_to_ui(self, path: Path) -> str:
        return str(path)
