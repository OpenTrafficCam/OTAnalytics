import platform
from pathlib import Path
from typing import Any

from nicegui import events, ui

OK_BUTTON_NAME = "Ok"
CANCEL_BUTTON_NAME = "Cancel"
DATA = "data"
NAME = "name"
PATH = "path"
FILE = "File"
ROW_DATA = "rowData"
NULL_TERMINATOR = "\000"


class LocalFilePicker(ui.dialog):

    def __init__(
        self,
        directory: Path,
        *,
        multiple: bool = False,
        show_hidden_files: bool = False,
        show_files_only_of_type: str | None = None,
        show_only_directories: bool = False,
    ) -> None:
        """Local File Picker

        This is a simple file picker that allows you to select a file from the local
        filesystem where NiceGUI is running.

        Args:
            directory (Path): The directory to start in.
            multiple (bool): Whether to allow multiple files to be selected.
            show_hidden_files (bool): Whether to show hidden files.
            show_files_only_of_type (str): Show files only of type specified.
                Otherwise, show all files.
            show_only_directories (bool): Whether to show only directories.
                If True, files will not be shown in the picker.
        """
        super().__init__()

        self.path = directory.expanduser()
        self.upper_limit = directory.expanduser()
        self.show_hidden_files = show_hidden_files
        self.show_files_only_of_type = show_files_only_of_type
        self.show_only_directories = show_only_directories

        with self, ui.card().style("max-width: 70%; width: 100%"):
            self.add_drives_toggle()
            with ui.row().classes("w-full"):
                self.path_input = ui.input(
                    label="Path",
                    value=str(self.path),
                    on_change=self.update_path_from_input,
                ).classes("w-full")
            self.grid = ui.aggrid(
                {
                    "columnDefs": [{"field": NAME, "headerName": FILE}],
                    "rowSelection": "multiple" if multiple else "single",
                },
                html_columns=[0],
            ).on("cellDoubleClicked", self.handle_double_click)
            with ui.row().classes("w-full justify-end"):
                ui.button(CANCEL_BUTTON_NAME, on_click=self.close).props("outline")
                ui.button(OK_BUTTON_NAME, on_click=self._handle_ok)
        self.update_grid()

    def add_drives_toggle(self) -> None:
        if platform.system() == "Windows":
            import win32api

            drives = win32api.GetLogicalDriveStrings().split(NULL_TERMINATOR)[:-1]
            self.drives_toggle = ui.toggle(
                drives, value=drives[0], on_change=self.update_drive
            )

    def update_drive(self) -> None:
        self.path = Path(self.drives_toggle.value).expanduser()
        self.path_input.value = str(self.path)
        self.update_grid()

    def update_path_from_input(self, e: Any) -> None:
        try:
            new_path = Path(e.value).expanduser()
            if new_path.exists() and new_path.is_dir():
                self.path = new_path
                self.update_grid()
            else:
                # If path doesn't exist or is not a directory, revert to current path
                self.path_input.value = str(self.path)
        except Exception:
            # If there's any error, revert to current path
            self.path_input.value = str(self.path)

    def update_grid(self) -> None:
        paths = list(self.path.glob("*"))
        if not self.show_hidden_files:
            paths = [p for p in paths if not p.name.startswith(".")]

        if self.show_only_directories:
            paths = [p for p in paths if p.is_dir()]
        elif self.show_files_only_of_type:
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
        rows = await self.grid.get_selected_rows()
        paths = [self._map_to_domain(r[PATH]) for r in rows]

        # If no rows are selected and we're in directory-only mode, use the current directory # noqa
        if not paths and self.show_only_directories:
            paths = [self.path]

        self.submit(paths)

    def _map_to_domain(self, path: str) -> Path:
        return Path(path)

    def _map_to_ui(self, path: Path) -> str:
        return str(path)
