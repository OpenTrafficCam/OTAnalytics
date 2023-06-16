LINE_COLOR: str = "outline"
"""Specifies the line colour.
The given value may be any valid Tk colour.
If the value is an empty string, then the line will be transparent.
The default values are as follows:
    MacOS & Windows: platform default foreground colour
    Unix: black
"""

LINE_WIDTH: str = "width"
"""Specifies the width of the line or outline.
Only applied in combination wit LINE_COLOR.
The default value is 1."""

LINE_DASH: str = "dash"
"""Specifies dash patterns of the line (correspondingly).
The value may be any valid Tk dash style. The default value is a solid line."""

LINE_DASH_OFFSET: str = "dashoffset"
"""The starting offset in pixels into the pattern provided by the dash option.
Is ignored if there is no dash pattern.
The offset may have any of the forms described in the coordinates section below.
The default value is 0."""

LINE_CAPS: str = "capstyle"
"""Specifies the ways in which caps are to be drawn at the endpoints of the line.
The value may be any of butt, projecting, or round. Where arrowheads are drawn,
the cap style is ignored.
The default value is butt."""

FILL_COLOR: str = "fill"
"""Specifies the colour to be used to fill item's area.
The given value may be any valid Tk colour.
If the value is an empty string, then the item will not be transparent.
The default value is an empty string."""

RADIUS: str = "radius"
"""Radius of a circle on the tkinter canvas"""

ARROWSHAPE: str = "arrowshape"
"""A tuple of three values representing the shape of the arrow.
The values are (length, width at base, width at tip)."""

LINE: str = "line"
"""A line representing a segment of a MultiLineSection"""

KNOB: str = "knob"
"""A combination of canvas items containing a filled circle and a perimeter around it
representing a coordinate of a MultiLinesection"""

KNOB_CORE: str = "knob-core"
"""A filled circle representing a knob itself"""

KNOB_PERIMETER: str = "knob-perimeter"
"""A circle around a knob to indicate if it is hovered or selected"""

SECTION_TEXT: str = "section-text"
"""A text displayed above the section"""

DEFAULT_SECTION_STYLE = {
    LINE: {FILL_COLOR: "#47936B", LINE_WIDTH: 3},
    KNOB: {
        KNOB_CORE: {FILL_COLOR: "#47936B", LINE_WIDTH: 0, RADIUS: 1.5},
    },
}

SELECTED_SECTION_STYLE = {
    LINE: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 4},
    KNOB: {
        KNOB_CORE: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 0, RADIUS: 2},
    },
}

PRE_EDIT_SECTION_STYLE = {
    LINE: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 2, LINE_DASH: (5, 5)},
    KNOB: {
        KNOB_CORE: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 0, RADIUS: 1},
    },
}

EDITED_SECTION_STYLE = {
    LINE: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 4},
    KNOB: {
        KNOB_CORE: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 0, RADIUS: 6},
    },
}

HOVERED_KNOB_STYLE = {
    KNOB_CORE: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 0, RADIUS: 6},
    KNOB_PERIMETER: {LINE_COLOR: "#8CFFC2", LINE_WIDTH: 2, RADIUS: 10},
}

SELECTED_KNOB_STYLE = {
    KNOB_CORE: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 0, RADIUS: 6},
    KNOB_PERIMETER: {LINE_COLOR: "#8CFFC2", LINE_WIDTH: 2, RADIUS: 10},
}

ARROW_STYLE = {
    FILL_COLOR: "#8CFFC2",
    LINE_WIDTH: 4,
    LINE_DASH: (5, 5),
    ARROWSHAPE: (20, 25, 8),
}

COLOR_GREEN = "green"
COLOR_RED = "red"
COLOR_ORANGE = "orange"
COLOR_GRAY = "gray"
STICKY_WEST = "W"
ANCHOR_WEST = "w"
