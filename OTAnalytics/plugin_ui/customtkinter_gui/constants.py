from dataclasses import dataclass
from typing import ClassVar

from OTAnalytics.application.config import ON_MAC

PADX = 10
PADY = 5
TABVIEW_SEGMENTED_BUTTON_ELEVATION = 13
STICKY = "NESW"

LEFT_BUTTON_DOWN = "left_mousebutton_down"
LEFT_BUTTON_UP = "left_mousebutton_up"
RIGHT_BUTTON_UP = "right_mousebutton_up"
MOTION = "mouse_motion"
MOTION_WHILE_LEFT_BUTTON_DOWN = "mouse_motion_while_left_button_down"
LEAVE_CANVAS = "mouse_leaves_canvas"
ENTER_CANVAS = "mouse_enters_canvas"
RETURN_KEY = "return"
DELETE_KEYS = "delete"
ESCAPE_KEY = "escape"
LEFT_KEY = "left"
RIGHT_KEY = "right"
PLUS_KEYS = "+"
MINUS_KEYS = "-"

STATE_DISABLED = "disabled"
STATE_NORMAL = "normal"


@dataclass
class TkEvents:
    """
    Class holding tkinter events as class properties.
    The strings behind some of the events depend on the platform the software is
    running on (Linux, Mac, or Windows).
    """

    RIGHT_BUTTON_DOWN: ClassVar[str] = "<Button-2>" if ON_MAC else "<Button-3>"
    RIGHT_BUTTON_UP: ClassVar[str] = (
        "<ButtonRelease-2>" if ON_MAC else "<ButtonRelease-3>"
    )
    MIDDLE_BUTTON_DOWN: ClassVar[str] = "<Button-3>" if ON_MAC else "<Button-2>"
    MIDDLE_BUTTON_UP: ClassVar[str] = (
        "<ButtonRelease-3>" if ON_MAC else "<ButtonRelease-2>"
    )
    LEFT_BUTTON_DOWN: ClassVar[str] = "<Button-1>"
    LEFT_BUTTON_UP: ClassVar[str] = "<ButtonRelease-1>"
    LEFT_BUTTON_DOUBLE: ClassVar[str] = "<Double-1>"
    MOUSE_MOTION: ClassVar[str] = "<Motion>"
    MOUSE_MOTION_WHILE_LEFT_BUTTON_DOWN: ClassVar[str] = "<B1-Motion>"
    MOUSE_ENTERS_WIDGET: ClassVar[str] = "<Enter>"
    MOUSE_LEAVES_WIDGET: ClassVar[str] = "<Leave>"
    TREEVIEW_SELECT: ClassVar[str] = "<<TreeviewSelect>>"
    PLUS_KEY: ClassVar[str] = "+"
    KEYPAD_PLUS_KEY: ClassVar[str] = "<KP_Add>"
    LEFT_ARROW_KEY: ClassVar[str] = "<Left>"
    RIGHT_ARROW_KEY: ClassVar[str] = "<Right>"
    UP_ARROW_KEY: ClassVar[str] = "<Up>"
    DOWN_ARROW_KEY: ClassVar[str] = "<Down>"
    RETURN_KEY: ClassVar[str] = "<Return>"
    KEYPAD_RETURN_KEY: ClassVar[str] = "<KP_Enter>"
    DELETE_KEY: ClassVar[str] = "<Delete>"
    BACKSPACE_KEY: ClassVar[str] = "<BackSpace>"
    ESCAPE_KEY: ClassVar[str] = "<Escape>"
    MULTI_SELECT_SINGLE: ClassVar[str] = (
        "<Command-ButtonRelease-1>" if ON_MAC else "<Control-ButtonRelease-1>"
    )


tk_events = TkEvents()
