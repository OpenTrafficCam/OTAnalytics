from tkinter import Widget


def get_widget_position(widget: Widget) -> tuple[int, int]:
    x = widget.winfo_rootx()
    y = widget.winfo_rooty()
    return x, y
