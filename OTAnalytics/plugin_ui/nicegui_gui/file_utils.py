"""Utility functions for file operations in the NiceGUI UI."""

from pathlib import Path
from typing import Callable

from OTAnalytics.plugin_ui.nicegui_gui.dialogs.file_picker import LocalFilePicker


async def select_output_directory(
    directory: Path, set_directory_callback: Callable[[str], None]
) -> None:
    """Open a dialog to browse for a directory.

    Args:
        directory: The current directory path
        set_directory_callback: Callback function to set the directory value
    """
    # Use LocalFilePicker to browse for a directory
    picker = LocalFilePicker(
        directory=directory,
        show_hidden_files=False,
        show_only_directories=True,
    )
    result = await picker
    if result and result[0]:
        # If the selected path is a directory, use it directly
        # Otherwise, use its parent directory
        selected_path = result[0]
        if selected_path.is_dir():
            set_directory_callback(str(selected_path))
        else:
            set_directory_callback(str(selected_path.parent))
