from tkinter import Widget


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


def get_widget_position(widget: Widget) -> tuple[int, int]:
    """Returns the current position of a tkinter (or customtkinter) widget.

    Args:
        widget (Widget): tkinter (or customtkinter) widget

    Returns:
        tuple[int, int]: Tuple of x and y coordinates of top-left corner of the widget
    """
    x = widget.winfo_rootx()
    y = widget.winfo_rooty()
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
