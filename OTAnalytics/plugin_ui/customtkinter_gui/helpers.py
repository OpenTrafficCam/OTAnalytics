from pathlib import Path
from tkinter import Widget
from tkinter.filedialog import asksaveasfilename
from typing import Any

from OTAnalytics.adapter_ui.helpers import ensure_file_extension_is_present


class InvalidReferenceError(Exception):
    pass


def get_widget_size(widget: Widget) -> tuple[int, int]:
    """Returns the current size of a tkinter (or customtkinter) widget.

    Args:
        widget (Widget): tkinter (or customtkinter) widget

    Returns:
        tuple[int, int]: Tuple of width and height of the widget
    """
    width = widget.winfo_width()
    height = widget.winfo_height()
    return width, height


def get_widget_position(
    widget: Widget, offset: tuple[float, float] = (0.5, 0.5)
) -> tuple[int, int]:
    """Returns the current position of a tkinter (or customtkinter) widget.

    Args:
        widget (Widget): Tkinter or customtkinter widget
        offset (tuple[float, float], optional): Relative offset of the widget.
            E.g. (0, 0) gives top left and (1, 1) gives bottom right corner.
            Each value has to be >=0 and <=1.
            Defaults to (0.5, 0.5).

    Raises:
        InvalidReferenceError: If horizontal offset is < 0 or > 1
        InvalidReferenceError: If vertical offset is < 0 or > 1

    Returns:
        tuple[int, int]: Tuple of x and y coordinates of the widget
    """

    offset_x, offset_y = offset
    if offset_x < 0 or offset_x > 1:
        raise InvalidReferenceError(
            f"Horizontal widget reference has to be >=0 and <=1, but is {offset_x}"
        )
    if offset_y < 0 or offset_y > 1:
        raise InvalidReferenceError(
            f"Vertical widget reference has to be >=0 and <=1, but is {offset_y}"
        )
    x0 = widget.winfo_rootx()
    y0 = widget.winfo_rooty()
    w = widget.winfo_width()
    h = widget.winfo_height()
    x = round(x0 + offset_x * w)
    y = round(y0 + offset_y * h)
    return x, y


def get_mouse_position(widget: Widget) -> tuple[int, int]:
    """Returns the current position of the mouse on a tkinter (or customtkinter) widget.

    Args:
        widget (Widget): Tkinter or customtkinter widget

    Returns:
        tuple[int, int]: Tuple of x and y coordinates of mouse on the widget
    """
    x = widget.winfo_pointerx()
    y = widget.winfo_pointery()
    return x, y


def coordinate_is_on_widget(
    coordinate_relative_to_widget: tuple[int, int], widget: Widget
) -> bool:
    """Returns True, if the coordinate is within the boundaries of an existing
        tkinter (or customtkinter) widget.

    Args:
        coordinate (tuple[int, int]): Coordinate relative to the widget position.
            E.g. for the tkinter/customtkinter canvas, absolute coordinates have to be
            transformed to relative coordinates using Canvas.canvasx(absolute_x) as well
            as Canvas.canvasy(absolute_y).

        widget (Widget): Tkinter or customtkinter Widget

    Returns:
        bool: True if the coordinate is within tho boundaries of the widget,
            false otherwise.
    """
    widget_width, widget_heigt = get_widget_size(widget)
    x, y = coordinate_relative_to_widget
    left_in = x >= 0
    right_in = x <= widget_width
    top_in = y >= 0
    bottom_in = y <= widget_heigt
    return False not in [left_in, right_in, top_in, bottom_in]


def ask_for_save_file_path(
    title: str,
    filetypes: list[tuple[str, str]],
    defaultextension: str,
    **kwargs: Any,
) -> Path:
    """
    Ask for a filename and ensure the file contains a file extension. If no extension
    is present, the default extension will be appended.

    Args:
        title (str): title for the file chooser
        file_types (list[tuple[str, str]]): supported file types to choose from
        defaultextension (str): default extension used if none is present

    Returns:
        Path: path object representing an output path
    """
    filename_with_extension = ask_for_save_file_name(
        title, filetypes, defaultextension, **kwargs
    )
    return Path(filename_with_extension)


def ask_for_save_file_name(
    title: str,
    filetypes: list[tuple[str, str]],
    defaultextension: str,
    **kwargs: Any,
) -> str:
    """
    Ask for a filename and ensure the file contains a file extension. If no extension
    is present, the default extension will be appended.

    Args:
        title (str): title for the file chooser
        file_types (list[tuple[str, str]]): supported file types to choose from
        defaultextension (str): default extension used if none is present

    Returns:
        str: file name with extension
    """
    filename = asksaveasfilename(
        title=title,
        filetypes=filetypes,
        defaultextension=defaultextension,
        **kwargs,
    )
    if filename:
        allowed_extensions = [filetype[1] for filetype in filetypes]
        return ensure_file_extension_is_present(
            filename, allowed_extensions, defaultextension
        )
    else:
        return filename
