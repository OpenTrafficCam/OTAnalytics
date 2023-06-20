from tkinter import Widget


class InvalidReferenceError(Exception):
    pass


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
