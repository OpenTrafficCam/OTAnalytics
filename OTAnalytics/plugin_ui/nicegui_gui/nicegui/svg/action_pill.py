from dataclasses import dataclass
from html import escape

from OTAnalytics.plugin_ui.nicegui_gui.nicegui.svg.primitives import screen_px

FINISH_SUFFIX = "finish"
CANCEL_SUFFIX = "cancel"
BACKGROUND_SUFFIX = "background"

PILL_CLASS = "ota-action"
BACKGROUND_CLASS = "background"
BUTTON_CLASS = "button"
FINISH_CLASS = "finish"
DISABLED_CLASS = "disabled"
CANCEL_CLASS = "cancel"
GLYPH_CLASS = "glyph"

# Sizes in screen pixels
BUTTON_RADIUS = 14
BUTTON_SPACING = 17
HEIGHT = 2 * BUTTON_RADIUS + 4
WIDTH = 2 * BUTTON_SPACING + 2 * BUTTON_RADIUS + 4

CHECK_PATH = "M-5 0L-1.5 4L5-4"
CROSS_PATH = "M-4-4L4 4M4-4L-4 4"


@dataclass
class ActionPill:
    """Pill with a button to finish and a button to cancel the section editor.

    x and y are the center of the pill in the image. Its size is in screen
    pixels. The finish button is drawn disabled, but stays clickable, as long as
    the section cannot be finished. Colours are set by otanalytics.css.
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
        finish_classes = f"{BUTTON_CLASS} {FINISH_CLASS}"
        if not self.finish_enabled:
            finish_classes += f" {DISABLED_CLASS}"
        inner = (
            f'<rect id="{escape(self.background_id)}" class="{BACKGROUND_CLASS}" '
            f'x="{-WIDTH // 2}" y="{-HEIGHT // 2}" width="{WIDTH}" '
            f'height="{HEIGHT}" rx="{HEIGHT // 2}"/>'
            + self._button(
                self.finish_id, finish_classes, -BUTTON_SPACING, self.finish_tooltip
            )
            + self._glyph(-BUTTON_SPACING, CHECK_PATH)
            + self._button(
                self.cancel_id,
                f"{BUTTON_CLASS} {CANCEL_CLASS}",
                BUTTON_SPACING,
                self.cancel_tooltip,
            )
            + self._glyph(BUTTON_SPACING, CROSS_PATH)
        )
        return screen_px(self.x, self.y, inner, PILL_CLASS)

    @staticmethod
    def _button(id: str, css_class: str, x: int, tooltip: str) -> str:
        return (
            f'<circle id="{escape(id)}" class="{css_class}" cx="{x}" cy="0" '
            f'r="{BUTTON_RADIUS}"><title>{escape(tooltip)}</title></circle>'
        )

    @staticmethod
    def _glyph(x: int, path: str) -> str:
        return f'<path class="{GLYPH_CLASS}" d="{path}" transform="translate({x} 0)"/>'
