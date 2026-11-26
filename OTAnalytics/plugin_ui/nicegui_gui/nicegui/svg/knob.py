from dataclasses import dataclass

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import dot, screen_px

EDIT_KNOB_ID_PREFIX = "edit-knob-"


@dataclass
class Knob:
    """Point of the section geometry editor.

    The number is the position of the knob in the section, starting at 1, unless
    another number is given, e.g. the position after a previewed shift. It is
    drawn inside the knob in screen pixels. A partner is the knob that swaps
    with the moving one in the shift preview.

    Only the hit path receives pointer events. It carries the id, by which the
    canvas recognizes the knob. The hit path of a moving knob is large, so the
    svg keeps receiving pointer events while the knob follows the mouse.
    """

    index: int
    x: int
    y: int
    active: bool = False
    moving: bool = False
    partner: bool = False
    number: int | None = None

    def to_svg(self) -> str:
        states = [
            ("active", self.active),
            ("moving", self.moving),
            ("partner", self.partner),
        ]
        classes = " ".join(["ota-knob"] + [name for name, on in states if on])
        paths = "".join(dot(self.x, self.y, part) for part in ["halo", "ring", "core"])
        shown = self.index + 1 if self.number is None else self.number
        number = screen_px(self.x, self.y, f'<text class="num">{shown}</text>')
        hit = dot(self.x, self.y, "hit", f"{EDIT_KNOB_ID_PREFIX}{self.index}")
        return f'<g class="{classes}">{paths}{number}{hit}</g>'
