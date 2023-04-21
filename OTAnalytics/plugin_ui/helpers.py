from tkinter import Widget


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
