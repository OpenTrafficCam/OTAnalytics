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

LINE: str = "line"
"""A line element of the ui representation of a section"""

KNOB: str = "knob"
"""A round knob element of the ui representation of a section"""

DEFAULT_SECTION_STYLE = {
    LINE: {FILL_COLOR: "#47936B", LINE_WIDTH: 3},
    # KNOB: {FILL_COLOR: "#47936B", LINE_WIDTH: 0, RADIUS: 5},
}

SELECTED_SECTION_STYLE = {
    LINE: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 4},
    # KNOB: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 0, RADIUS: 6},
}

EDITED_SECTION_STYLE = {
    LINE: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 4, LINE_DASH: "-"},
    KNOB: {FILL_COLOR: "#8CFFC2", LINE_WIDTH: 0, RADIUS: 6},
}
