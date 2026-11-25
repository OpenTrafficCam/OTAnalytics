from dataclasses import dataclass
from html import escape

FINISH_SUFFIX = "finish"
CANCEL_SUFFIX = "cancel"
BACKGROUND_SUFFIX = "background"

PILL_CLASS = "ota-action-pill"
BUTTON_CLASS = "ota-action-button"
FINISH_CLASS = "ota-action-finish"
FINISH_DISABLED_CLASS = "ota-action-disabled"
CANCEL_CLASS = "ota-action-cancel"
GLYPH_CLASS = "ota-action-glyph"

BUTTON_RADIUS = 14
BUTTON_SPACING = 17
HEIGHT = 2 * BUTTON_RADIUS + 4
WIDTH = 2 * BUTTON_SPACING + 2 * BUTTON_RADIUS + 4


@dataclass
class ActionPill:
    """Pill with a button to finish and a button to cancel the section editor.

    x and y are the center of the pill. The finish button is drawn disabled, but
    stays clickable, as long as the section cannot be finished.
    """

    id: str
    x: int
    y: int
    finish_enabled: bool = True
    finish_tooltip: str = ""
    cancel_tooltip: str = ""

    @property
    def finish_id(self) -> str:
        return f"{self.id}-{FINISH_SUFFIX}"

    @property
    def cancel_id(self) -> str:
        return f"{self.id}-{CANCEL_SUFFIX}"

    @property
    def background_id(self) -> str:
        return f"{self.id}-{BACKGROUND_SUFFIX}"

    def to_svg(self) -> str:
        finish_x = self.x - BUTTON_SPACING
        cancel_x = self.x + BUTTON_SPACING
        finish_class = (
            f"{BUTTON_CLASS} {FINISH_CLASS}"
            if self.finish_enabled
            else f"{BUTTON_CLASS} {FINISH_CLASS} {FINISH_DISABLED_CLASS}"
        )
        return (
            f'<rect id="{escape(self.background_id)}" class="{PILL_CLASS}" '
            f'x="{self.x - WIDTH // 2}" y="{self.y - HEIGHT // 2}" '
            f'width="{WIDTH}" height="{HEIGHT}" rx="{HEIGHT // 2}" '
            f'fill="white" pointer-events="all" />'
            + self._button(self.finish_id, finish_class, finish_x, self.finish_tooltip)
            + self._glyph(finish_x, "M -5 0 L -1.5 4 L 5 -4")
            + self._button(
                self.cancel_id,
                f"{BUTTON_CLASS} {CANCEL_CLASS}",
                cancel_x,
                self.cancel_tooltip,
            )
            + self._glyph(cancel_x, "M -4 -4 L 4 4 M 4 -4 L -4 4")
        )

    def _button(self, id: str, css_class: str, x: int, tooltip: str) -> str:
        return (
            f'<circle id="{escape(id)}" class="{css_class}" cx="{x}" cy="{self.y}" '
            f'r="{BUTTON_RADIUS}" fill="gray" pointer-events="all" cursor="pointer">'
            f"<title>{escape(tooltip)}</title></circle>"
        )

    def _glyph(self, x: int, path: str) -> str:
        return (
            f'<path class="{GLYPH_CLASS}" d="{path}" '
            f'transform="translate({x} {self.y})" fill="none" stroke="white" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
            f'pointer-events="none" />'
        )
