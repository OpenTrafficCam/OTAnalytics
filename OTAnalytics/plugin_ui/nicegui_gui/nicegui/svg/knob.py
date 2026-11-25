from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import dot

EDIT_KNOB_ID_PREFIX = "edit-knob-"


@dataclass
class Knob:
    """Point of the section geometry editor.

    Only the hit path receives pointer events. It carries the id, by which the
    canvas recognizes the knob. The hit path of a moving knob is large, so the
    svg keeps receiving pointer events while the knob follows the mouse.
    """

    index: int
    x: int
    y: int
    active: bool = False
    moving: bool = False

    def to_svg(self) -> str:
        states = [("active", self.active), ("moving", self.moving)]
        classes = " ".join(["ota-knob"] + [name for name, on in states if on])
        paths = "".join(dot(self.x, self.y, part) for part in ["halo", "ring", "core"])
        hit = dot(self.x, self.y, "hit", f"{EDIT_KNOB_ID_PREFIX}{self.index}")
        return f'<g class="{classes}">{paths}{hit}</g>'
